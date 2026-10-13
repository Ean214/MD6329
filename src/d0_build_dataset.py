# -*- coding: utf-8 -*-
"""
MD6329 Deep Learning for Healthcare AI -- final course project.
Generative AI assistance was used in writing this script, as disclosed in the
report (Section 4, "Software 3.0") and on the project cover page. The author
validated the implementation and the results, and remains responsible for both.
"""
"""D0: build modeling dataset from HEMOBP (memory-optimized, int keys).

Sample unit = (session, prediction time T). Input = readings with time<=T,
target = nadir SBP<90 among readings with time>T. Excludes sessions already
hypotensive before T. Leakage-safe by construction.

Outputs (per horizon T in {30,60,90,120}):
  data/tabular_T{T}.pkl      engineered features + y + pid + split
  data/seq_T{T}.npz          X_seq[N,96,7], mask[N,96], X_stat[N,15], y, pid, split
  results/protocol.json
"""
import json, os, sys, time
import numpy as np, pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import BASE, DATA, RESULTS, SEED, patient_split, save_json

HORIZONS = [30, 60, 90, 120]
L_MAX = 96
SEQ_FEATS = ["sbp", "dbp", "uf", "blood_flow", "conductivity", "dia_temp_value", "dt_norm"]
STAT_FEATS = ["T_min", "age", "gender_m", "DM", "weightstart", "dryweight", "idwg",
              "first_sbp", "nadir_so_far", "slope_sbp", "mean_uf_so_far",
              "mean_bf_so_far", "mean_cond_so_far", "mean_temp_so_far", "n_bp_so_far"]

def load():
    print("[d0] loading sessions.csv ...", flush=True)
    sess = pd.read_csv(os.path.join(RESULTS, "sessions.csv"))
    before = len(sess)
    sess = sess[(sess["duration_min"] >= 60) & (sess["duration_min"] <= 480)]
    sess = sess[(sess["weightstart"] >= 20) & (sess["weightstart"] <= 200)]
    sess = sess[(sess["idwg"] >= -2) & (sess["idwg"] <= 10)]
    sess = sess[(sess["ufr_ml_kg_h"] >= 0) & (sess["ufr_ml_kg_h"] <= 20)]
    print(f"[d0] sessions {before:,} -> {len(sess):,} after cleaning", flush=True)

    print("[d0] loading vip.csv ...", flush=True)
    vip = pd.read_csv(os.path.join(BASE, "hemobp", "vip.csv"),
                      usecols=["pid", "datatime", "time", "sbp", "dbp", "uf",
                               "blood_flow", "conductivity", "dia_temp_value"],
                      dtype={"sbp": "float32", "dbp": "float32", "uf": "float32",
                             "blood_flow": "float32", "conductivity": "float32",
                             "dia_temp_value": "float32", "time": "float32"})
    vip["datatime"] = pd.to_datetime(vip["datatime"], errors="coerce")
    vip = vip.dropna(subset=["datatime"]).sort_values(["pid", "datatime"], kind="mergesort")
    gap_min = vip.groupby("pid")["datatime"].diff().dt.total_seconds().div(60)
    new_sess = (gap_min > 360) | gap_min.isna()
    vip["sessnum"] = new_sess.groupby(vip["pid"]).cumsum().astype("int32")
    vip = vip.drop(columns=["datatime"])
    vip["dt_norm"] = (vip["time"] / 240.0).astype("float32")
    return sess, vip

def build_T(sess, vip, T):
    t0 = time.time()
    meta = sess[sess["duration_min"] >= T + 30][
        ["pid", "sessnum", "weightstart", "dryweight", "idwg",
         "age", "gender", "DM"]].copy()
    meta["gender_m"] = (meta["gender"] == "M").astype("float32")
    v = vip.merge(meta, on=["pid", "sessnum"], how="inner")
    v = v.sort_values(["pid", "sessnum", "time"], kind="mergesort")

    # --- numpy vectorization: session boundaries then pure-array slicing ---
    key = v["pid"].to_numpy() * 100000 + v["sessnum"].to_numpy()
    order = np.arange(len(v))  # already sorted by (pid, sessnum, time)
    change = np.empty(len(v), dtype=bool)
    change[0] = True
    change[1:] = key[1:] != key[:-1]
    starts = np.flatnonzero(change)
    ends = np.append(starts[1:], len(v))

    cols = {c: v[c].to_numpy() for c in
            ["time", "sbp", "dbp", "uf", "blood_flow", "conductivity",
             "dia_temp_value", "dt_norm", "age", "gender_m", "DM",
             "weightstart", "dryweight", "idwg"]}
    pid_arr = v["pid"].to_numpy()
    sn_arr = v["sessnum"].to_numpy()

    X_seq, M, X_stat, Y, PID, SN, UFP, REM = [], [], [], [], [], [], [], []
    for a, b in zip(starts, ends):
        t = cols["time"][a:b]
        pre_m = t <= T
        n_pre = int(pre_m.sum()); n_post = int((~pre_m).sum())
        if n_pre < 3 or n_post == 0:
            continue
        i_pre = np.flatnonzero(pre_m)
        i_post = np.flatnonzero(~pre_m)
        sbp_pre = cols["sbp"][a:b][i_pre]
        if np.nanmin(sbp_pre) < 90:
            continue
        sbp_post = cols["sbp"][a:b][i_post]
        if np.all(np.isnan(sbp_post)):
            continue
        # sequence: last L_MAX pre rows
        idx = i_pre[-L_MAX:]
        x = np.empty((L_MAX, 7), dtype=np.float32)
        x.fill(0.0)
        mask = np.zeros(L_MAX, dtype=np.float32)
        n = len(idx)
        x[L_MAX - n:, 0] = cols["sbp"][a:b][idx]
        x[L_MAX - n:, 1] = cols["dbp"][a:b][idx]
        x[L_MAX - n:, 2] = cols["uf"][a:b][idx]
        x[L_MAX - n:, 3] = cols["blood_flow"][a:b][idx]
        x[L_MAX - n:, 4] = cols["conductivity"][a:b][idx]
        x[L_MAX - n:, 5] = cols["dia_temp_value"][a:b][idx]
        x[L_MAX - n:, 6] = cols["dt_norm"][a:b][idx]
        np.nan_to_num(x, copy=False)
        mask[L_MAX - n:] = 1.0
        # slope over distinct BP points
        slope = 0.0
        tt = t[i_pre]; ss = sbp_pre
        ok = ~(np.isnan(tt) | np.isnan(ss))
        tt = tt[ok]; ss = ss[ok]
        if len(tt) >= 2 and (tt.max() - tt.min()) > 0:
            keep = np.ones(len(tt), dtype=bool)
            keep[1:] = ss[1:] != ss[:-1]
            if keep.sum() >= 2:
                try:
                    slope = float(np.polyfit(tt[keep], ss[keep], 1)[0])
                except Exception:
                    slope = 0.0
        age = cols["age"][a]; dm = cols["DM"][a]
        stat = [float(T),
                float(age) if not np.isnan(age) else 65.0,
                float(cols["gender_m"][a]),
                float(dm) if not np.isnan(dm) else 0.0,
                float(cols["weightstart"][a]),
                float(cols["dryweight"][a]),
                float(cols["idwg"][a]),
                float(sbp_pre[0]),
                float(np.nanmin(sbp_pre)),
                float(slope),
                float(np.nanmean(cols["uf"][a:b][i_pre])),
                float(np.nanmean(cols["blood_flow"][a:b][i_pre])),
                float(np.nanmean(cols["conductivity"][a:b][i_pre])),
                float(np.nanmean(cols["dia_temp_value"][a:b][i_pre])),
                float(len(np.unique(ss[~np.isnan(ss)])))]
        X_seq.append(x); M.append(mask); X_stat.append(stat)
        Y.append(1 if float(np.nanmin(sbp_post)) < 90 else 0)
        PID.append(int(pid_arr[a])); SN.append(int(sn_arr[a]))
        UFP.append(float(np.nanmean(cols["uf"][a:b][i_post])))
        REM.append(float(max(t[i_post]) - T))
    dt = time.time() - t0
    X_seq = np.stack(X_seq); M = np.stack(M)
    X_stat = np.asarray(X_stat, dtype=np.float32)
    Y = np.asarray(Y, dtype=np.int64); PID = np.asarray(PID)
    SN = np.asarray(SN); UFP = np.asarray(UFP, dtype=np.float32)
    REM = np.asarray(REM, dtype=np.float32)
    return X_seq, M, X_stat, Y, PID, SN, UFP, REM, dt

def main():
    sess, vip = load()
    split = patient_split()
    save_json({"seed": SEED, "split_rule": "by pid 70/15/15",
               "horizons": HORIZONS, "L_MAX": L_MAX,
               "seq_feats": SEQ_FEATS, "stat_feats": STAT_FEATS,
               "target": "nadir SBP<90 among readings with time>T",
               "cleaning": "duration[60,480], weight[20,200], idwg[-2,10], ufr[0,20]; exclude already-hypotensive pre-T; require >=3 readings pre-T and >=1 post-T"},
              "protocol.json")
    os.makedirs(DATA, exist_ok=True)
    for T in HORIZONS:
        X_seq, M, X_stat, Y, PID, SN, UFP, REM, dt = build_T(sess, vip, T)
        sp = np.array([split[p] for p in PID])
        np.savez_compressed(os.path.join(DATA, f"seq_T{T}.npz"),
                            X_seq=X_seq, mask=M, X_stat=X_stat, y=Y, pid=PID,
                            sessnum=SN, mean_uf_post=UFP, remaining_min=REM, split=sp)
        tab = pd.DataFrame(X_stat, columns=STAT_FEATS)
        tab["y"] = Y; tab["pid"] = PID; tab["sessnum"] = SN
        tab["mean_uf_post"] = UFP; tab["remaining_min"] = REM; tab["split"] = sp
        tab.to_pickle(os.path.join(DATA, f"tabular_T{T}.pkl"))
        print(f"[d0] T={T}: N={len(Y):,} train={(sp=='train').sum():,} "
              f"IDH_rate={Y.mean():.4f} ({dt:.0f}s)", flush=True)
        del X_seq, M, X_stat, Y, PID, SN, UFP, REM, sp, tab
    print("DONE", flush=True)

if __name__ == "__main__":
    main()
