# -*- coding: utf-8 -*-
"""
MD6329 Deep Learning for Healthcare AI -- final course project.
Generative AI assistance was used in writing this script, as disclosed in the
report (Section 4, "Software 3.0") and on the project cover page. The author
validated the implementation and the results, and remains responsible for both.
"""
"""E3: prediction-horizon curve (C1) + E4: modality ablation (C3).
E3 writes results/e3_horizon.json + results/fig_e3_horizon.png
E4 writes results/e4_ablation.json + results/fig_e4_ablation.png
Usage: python e3_e4.py [e3|e4|both]
"""
import json, os, sys
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import xgboost as xgb

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import DATA, RESULTS, STAT_FEATS, SEED, metrics, save_json

HORIZONS = [30, 60, 90, 120]

GROUPS = {
    "demo_static": ["age", "gender_m", "DM", "weightstart", "dryweight", "idwg"],
    "pre_bp": ["first_sbp", "nadir_so_far", "slope_sbp", "n_bp_so_far"],
    "machine": ["mean_uf_so_far", "mean_bf_so_far", "mean_cond_so_far", "mean_temp_so_far"],
}

def fit_eval(tab, feats):
    tr = tab[tab["split"] == "train"]; te = tab[tab["split"] == "test"]
    scale = float((tr["y"] == 0).sum()) / max(1, int((tr["y"] == 1).sum()))
    clf = xgb.XGBClassifier(n_estimators=600, max_depth=6, learning_rate=0.05,
                            subsample=0.8, colsample_bytree=0.8, min_child_weight=5,
                            scale_pos_weight=scale, tree_method="hist",
                            random_state=SEED, n_jobs=8, eval_metric="aucpr")
    clf.fit(tr[feats].to_numpy(), tr["y"].to_numpy())
    return metrics(te["y"].to_numpy(), clf.predict_proba(te[feats].to_numpy())[:, 1])

def e3():
    out = {"xgboost": {}, "cnnmlp": {}, "prevalence": {}}
    for T in HORIZONS:
        tab = pd.read_pickle(os.path.join(DATA, f"tabular_T{T}.pkl"))
        out["prevalence"][f"T{T}"] = round(float(tab[tab["split"] == "test"]["y"].mean()), 4)
        r = fit_eval(tab, STAT_FEATS)
        out["xgboost"][f"T{T}"] = {"auprc": r["auprc"], "auroc": r["auroc"],
                                   "lift_vs_prevalence": round(r["auprc"] / max(r["prevalence"], 1e-9), 2)}
        # NN arm (cnnmlp already trained per horizon by d1_nn.py if available)
        p = os.path.join(RESULTS, f"e1_cnnmlp_T{T}.json")
        if os.path.exists(p):
            d = json.load(open(p))
            out["cnnmlp"][f"T{T}"] = {"auprc": d["auprc"], "auroc": d["auroc"]}
    save_json(out, "e3_horizon.json")
    fig, ax = plt.subplots(figsize=(6.5, 4.2))
    xs = HORIZONS
    ax.plot(xs, [out["xgboost"][f"T{T}"]["auprc"] for T in xs], "o-", label="XGBoost")
    if out["cnnmlp"]:
        ys = [out["cnnmlp"].get(f"T{T}", {}).get("auprc") for T in xs]
        ax.plot(xs, ys, "s-", label="1D-CNN+MLP")
    ax.plot(xs, [out["prevalence"][f"T{T}"] for T in xs], "k--", label="prevalence (no-skill)")
    ax.set_xlabel("prediction time T into session (min)"); ax.set_ylabel("test AUPRC")
    ax.set_title("E3: predictability vs prediction time"); ax.legend()
    fig.tight_layout(); fig.savefig(os.path.join(RESULTS, "fig_e3_horizon.png"), dpi=130)
    print(json.dumps(out, indent=2))

def e4():
    T = 60
    tab = pd.read_pickle(os.path.join(DATA, f"tabular_T{T}.pkl"))
    out = {"horizon_T": T, "full": fit_eval(tab, STAT_FEATS)}
    for name, feats in GROUPS.items():
        extra = ["T_min"]
        out[f"only_{name}"] = fit_eval(tab, feats + extra)
        drop = [f for f in STAT_FEATS if f not in feats]
        out[f"without_{name}"] = fit_eval(tab, drop)
    save_json(out, "e4_ablation.json")
    labels = ["full", "only_demo_static", "only_pre_bp", "only_machine",
              "without_demo_static", "without_pre_bp", "without_machine"]
    vals = [out[k]["auprc"] for k in labels]
    fig, ax = plt.subplots(figsize=(7.5, 4.2))
    cols = ["#2a7"] + ["#5aa"] * 3 + ["#a55"] * 3
    ax.barh(labels, vals, color=cols)
    ax.axvline(out["full"]["auprc"], color="gray", ls="--", lw=1)
    for i, v in enumerate(vals):
        ax.text(v + 0.002, i, f"{v:.3f}", va="center", fontsize=8)
    ax.set_xlabel("test AUPRC (T=60)")
    ax.set_title("E4: modality ablation (green=all, light=only, red=left-out)")
    fig.tight_layout(); fig.savefig(os.path.join(RESULTS, "fig_e4_ablation.png"), dpi=130)
    print(json.dumps({k: v["auprc"] for k, v in out.items() if isinstance(v, dict)}, indent=2))

if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "both"
    if which in ("e3", "both"): e3()
    if which in ("e4", "both"): e4()
