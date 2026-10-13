# -*- coding: utf-8 -*-
"""P0: HEMOBP session reconstruction + EDA.
Session = contiguous readings per patient (gap > 6h starts new session).
Dialysis day = (session_start - 8h).date  (d1.keyindate is stamped 08:00:00).
Outputs: results/sessions.csv, results/eda_summary.json, results/fig_*.png
"""
import json, os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HEMOBP = os.path.join(BASE, "hemobp")
OUT = os.path.join(BASE, "results")
os.makedirs(OUT, exist_ok=True)
GAP_H = 6.0

def main():
    print("[1/6] reading vip.csv (needed cols)...", flush=True)
    vip = pd.read_csv(os.path.join(HEMOBP, "vip.csv"),
                      usecols=["pid", "datatime", "sbp", "dbp", "uf", "blood_flow"])
    vip["datatime"] = pd.to_datetime(vip["datatime"], errors="coerce")
    vip = vip.dropna(subset=["datatime"]).sort_values(["pid", "datatime"], kind="mergesort")
    print(f"  rows={len(vip):,} patients={vip['pid'].nunique():,}", flush=True)

    print("[2/6] session reconstruction...", flush=True)
    gap_min = vip.groupby("pid")["datatime"].diff().dt.total_seconds().div(60)
    new_sess = (gap_min > GAP_H * 60) | gap_min.isna()
    vip["sess"] = new_sess.groupby(vip["pid"]).cumsum()
    vip["sid"] = vip["pid"].astype(str) + "_" + vip["sess"].astype(str)

    print("[3/6] per-session aggregation...", flush=True)
    g = vip.groupby("sid")
    sess = pd.DataFrame({
        "pid": g["pid"].first(),
        "sessnum": g["sess"].first(),
        "start": g["datatime"].first(),
        "end": g["datatime"].last(),
        "n_readings": g.size(),
        "nadir_sbp": g["sbp"].min(),
        "max_sbp": g["sbp"].max(),
        "first_sbp": g["sbp"].first(),
        "mean_sbp": g["sbp"].mean(),
        "mean_dbp": g["dbp"].mean(),
        "mean_uf": g["uf"].mean(),
        "max_uf": g["uf"].max(),
        "mean_blood_flow": g["blood_flow"].mean(),
        "bp_n": g["sbp"].nunique(),
    })
    sess["duration_min"] = (sess["end"] - sess["start"]).dt.total_seconds().div(60)
    sess["drop_sbp"] = sess["max_sbp"] - sess["nadir_sbp"]
    # BP measurement interval: time between distinct BP values (per session)
    def bp_interval(sub):
        b = sub.drop_duplicates(subset=["sbp"])
        if len(b) < 2:
            return np.nan
        return b["datatime"].diff().dt.total_seconds().div(60).median()
    sess["bp_interval_med"] = g.apply(bp_interval)
    # dialysis day for joining d1
    sess["dialysis_date"] = (sess["start"] - pd.Timedelta(hours=8)).dt.date

    print("[4/6] join d1 (weights/dryweight) + idp (demographics)...", flush=True)
    d1 = pd.read_csv(os.path.join(HEMOBP, "d1.csv"))
    d1["keyindate"] = pd.to_datetime(d1["keyindate"], errors="coerce")
    d1["dialysis_date"] = d1["keyindate"].dt.date
    d1s = d1[["pid", "dialysis_date", "weightstart", "weightend", "dryweight", "temperature"]]
    d1s = d1s.dropna(subset=["dialysis_date"])
    sess = sess.merge(d1s, on=["pid", "dialysis_date"], how="left")
    idp = pd.read_csv(os.path.join(HEMOBP, "idp.csv"))
    sess = sess.merge(idp[["pid", "gender", "birthday", "DM"]], on="pid", how="left")
    sess["age"] = sess["start"].dt.year - pd.to_numeric(sess["birthday"], errors="coerce")
    sess["idwg"] = sess["weightstart"] - sess["dryweight"]
    sess["ufr_ml_kg_h"] = sess["mean_uf"] * 1000.0 / sess["weightstart"]

    # IDH definitions
    sess["idh_nadir90"] = sess["nadir_sbp"] < 90
    sess["idh_nadir100"] = sess["nadir_sbp"] < 100
    sess["idh_drop20"] = sess["drop_sbp"] >= 20

    print("[5/6] summary stats...", flush=True)
    joined = sess["weightstart"].notna()
    s = {
        "n_sessions": int(len(sess)),
        "n_patients": int(sess["pid"].nunique()),
        "session_duration_min": sess["duration_min"].describe().round(1).to_dict(),
        "bp_interval_med_min": float(np.nanmedian(sess["bp_interval_med"])),
        "d1_join_rate": round(float(joined.mean()), 3),
        "idp_join_rate": round(float(sess["gender"].notna().mean()), 3),
        "idwg_kg": sess.loc[joined, "idwg"].describe().round(2).to_dict(),
        "ufr_ml_kg_h": sess.loc[joined, "ufr_ml_kg_h"].describe().round(2).to_dict(),
        "idh_rates": {
            "nadir<90": round(float(sess["idh_nadir90"].mean()), 4),
            "nadir<100": round(float(sess["idh_nadir100"].mean()), 4),
            "drop>=20": round(float(sess["idh_drop20"].mean()), 4),
        },
        "nadh90_sessions": int(sess["idh_nadir90"].sum()),
        "age": sess["age"].describe().round(1).to_dict(),
        "dm_rate": round(float(sess["DM"].mean()), 3),
        "nadu2026": None,
    }
    s["nadu2026"] = None
    s.pop("nadu2026", None)
    with open(os.path.join(OUT, "eda_summary.json"), "w", encoding="utf-8") as f:
        json.dump(s, f, ensure_ascii=False, indent=2, default=str)
    sess.to_csv(os.path.join(OUT, "sessions.csv"), index=False)
    print(json.dumps(s, ensure_ascii=False, indent=2, default=str), flush=True)

    print("[6/6] figures...", flush=True)
    fig, ax = plt.subplots(figsize=(6, 4))
    sess["duration_min"].clip(0, 400).plot.hist(bins=60, ax=ax)
    ax.set_xlabel("session duration (min)"); ax.set_title("Session duration")
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "fig_duration.png"), dpi=120); plt.close(fig)

    fig, ax = plt.subplots(figsize=(6, 4))
    sess.loc[joined, "ufr_ml_kg_h"].clip(0, 30).plot.hist(bins=60, ax=ax)
    ax.axvline(13, color="r", ls="--", label="KDOQI 13 mL/kg/h")
    ax.set_xlabel("UFR (mL/kg/h)"); ax.set_title("Mean UFR per session"); ax.legend()
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "fig_ufr.png"), dpi=120); plt.close(fig)

    fig, ax = plt.subplots(figsize=(5, 4))
    rates = {k: v * 100 for k, v in s["idh_rates"].items()}
    ax.bar(rates.keys(), rates.values())
    ax.set_ylabel("IDH rate (%)"); ax.set_title("IDH incidence by definition")
    for i, (k, v) in enumerate(rates.items()):
        ax.text(i, v + 0.3, f"{v:.1f}%", ha="center")
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "fig_idh_rates.png"), dpi=120); plt.close(fig)

    fig, ax = plt.subplots(figsize=(6, 4))
    sess["bp_interval_med"].clip(0, 120).plot.hist(bins=60, ax=ax)
    ax.set_xlabel("median BP measurement interval (min)"); ax.set_title("BP sampling sparsity")
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "fig_bp_interval.png"), dpi=120); plt.close(fig)
    print("DONE", flush=True)

if __name__ == "__main__":
    main()
