# -*- coding: utf-8 -*-
"""
MD6329 Deep Learning for Healthcare AI -- final course project.
Generative AI assistance was used in writing this script, as disclosed in the
report (Section 4, "Software 3.0") and on the project cover page. The author
validated the implementation and the results, and remains responsible for both.

E8: probability calibration audit.

A reviewer objection we take seriously: every Brier score in E1 exceeds the
no-skill value p(1-p) = 0.0552, so the probabilities are unusable as risks even
though the ranking has signal. This script measures why and whether a simple
post-hoc recalibration repairs it:
  1. raw Brier vs no-skill baseline
  2. mean predicted probability vs observed prevalence
  3. calibration slope / intercept (logistic regression of y on logit p)
  4. Platt scaling fitted on VALIDATION and applied to TEST
  5. reliability diagram

Outputs results/e8_calibration.json + results/fig_e8_reliability.png
"""
import json, os, sys
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss, log_loss

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import DATA, RESULTS, STAT_FEATS, SEED, metrics, save_json

T = 60

def get_probs():
    """Return dict model -> (p_val, y_val, p_test, y_test)."""
    out = {}
    tab = pd.read_pickle(os.path.join(DATA, f"tabular_T{T}.pkl"))
    tr = tab[tab["split"] == "train"]; va = tab[tab["split"] == "val"]
    te = tab[tab["split"] == "test"]
    import xgboost as xgb
    scale = float((tr["y"] == 0).sum()) / max(1, int((tr["y"] == 1).sum()))
    m = xgb.XGBClassifier(n_estimators=600, max_depth=6, learning_rate=0.05,
                          subsample=0.8, colsample_bytree=0.8, min_child_weight=5,
                          scale_pos_weight=scale, tree_method="hist",
                          random_state=SEED, n_jobs=8, eval_metric="aucpr")
    m.fit(tr[STAT_FEATS].to_numpy(), tr["y"].to_numpy())
    out["xgboost"] = (m.predict_proba(va[STAT_FEATS].to_numpy())[:, 1], va["y"].to_numpy(),
                      m.predict_proba(te[STAT_FEATS].to_numpy())[:, 1], te["y"].to_numpy())

    import torch
    from d1_nn import MODELS, load_ds, standardize, DS, infer, DEV
    d = load_ds(T)
    Xf, M, Xst, y, sp, _ = standardize(d)
    for name in ["mlp", "cnnmlp", "lstm", "transformer"]:
        ck = os.path.join(RESULTS, f"ckpt_{name}_T{T}.pt")
        if not os.path.exists(ck):
            continue
        model = MODELS[name](Xf.shape[2], Xst.shape[1]).to(DEV)
        model.load_state_dict(torch.load(ck, map_location=DEV))
        pv, yv = infer(model, torch.utils.data.DataLoader(
            DS(Xf[sp == "val"], M[sp == "val"], Xst[sp == "val"], y[sp == "val"]), batch_size=512))
        pt, yt = infer(model, torch.utils.data.DataLoader(
            DS(Xf[sp == "test"], M[sp == "test"], Xst[sp == "test"], y[sp == "test"]), batch_size=512))
        out[name] = (pv, yv, pt, yt)
    return out

def calib_stats(p, y):
    eps = 1e-6
    lg = np.log(np.clip(p, eps, 1 - eps) / np.clip(1 - p, eps, 1 - eps)).reshape(-1, 1)
    lr = LogisticRegression(C=1e6, solver="lbfgs").fit(lg, y)
    return float(lr.coef_[0, 0]), float(lr.intercept_[0])

def platt(p_val, y_val, p_test):
    eps = 1e-6
    lg = np.log(np.clip(p_val, eps, 1 - eps) / np.clip(1 - p_val, eps, 1 - eps)).reshape(-1, 1)
    lr = LogisticRegression(C=1e6, solver="lbfgs").fit(lg, y_val)
    lt = np.log(np.clip(p_test, eps, 1 - eps) / np.clip(1 - p_test, eps, 1 - eps)).reshape(-1, 1)
    return lr.predict_proba(lt)[:, 1]

def main():
    probs = get_probs()
    te_prev = float(probs["xgboost"][3].mean())
    base_brier = te_prev * (1 - te_prev)
    res = {"test_prevalence": round(te_prev, 4),
           "no_skill_brier": round(base_brier, 4),
           "val_prevalence": round(float(probs["xgboost"][1].mean()), 4),
           "models": {}}
    for name, (pv, yv, pt, yt) in probs.items():
        slope, intercept = calib_stats(pt, yt)
        p_cal = platt(pv, yv, pt)
        res["models"][name] = {
            "mean_pred": round(float(pt.mean()), 4),
            "observed": round(float(yt.mean()), 4),
            "ratio": round(float(pt.mean() / max(yt.mean(), 1e-9)), 2),
            "brier_raw": round(float(brier_score_loss(yt, pt)), 4),
            "brier_baseline": round(base_brier, 4),
            "brier_platt": round(float(brier_score_loss(yt, p_cal)), 4),
            "logloss_raw": round(float(log_loss(yt, pt)), 4),
            "calib_slope": round(slope, 3),
            "calib_intercept": round(intercept, 3),
            "auprc_raw": round(float(metrics(yt, pt)["auprc"]), 4),
            "auprc_platt": round(float(metrics(yt, p_cal)["auprc"]), 4),
        }
        print(f"{name:12s} mean_p={pt.mean():.4f} obs={yt.mean():.4f} "
              f"Brier {res['models'][name]['brier_raw']:.4f} -> {res['models'][name]['brier_platt']:.4f} "
              f"| slope {slope:.2f}", flush=True)
    save_json(res, "e8_calibration.json")

    # reliability diagram (5 bins), raw vs Platt
    fig, axes = plt.subplots(1, 2, figsize=(9.5, 3.9))
    bins = np.linspace(0, 1, 6)
    for ax, (label, which) in zip(axes, [("raw", 0), ("Platt-recalibrated", 1)]):
        ax.plot([0, 1], [0, 1], color="#888780", ls="--", lw=1, label="perfect")
        for name, (pv, yv, pt, yt) in probs.items():
            p = pt if which == 0 else platt(pv, yv, pt)
            idx = np.digitize(p, bins) - 1
            xs, ys = [], []
            for b in range(len(bins) - 1):
                m = idx == b
                if m.sum() > 30:
                    xs.append(p[m].mean()); ys.append(yt[m].mean())
            ax.plot(xs, ys, "o-", ms=4, lw=1, label=name)
        ax.set_xlabel("mean predicted probability"); ax.set_ylabel("observed frequency")
        ax.set_title(f"E8: reliability, {label}", fontsize=10)
        ax.set_xlim(0, 0.8); ax.set_ylim(0, 0.8); ax.grid(alpha=0.3)
    axes[0].legend(fontsize=7)
    fig.tight_layout(); fig.savefig(os.path.join(RESULTS, "fig_e8_reliability.png"), dpi=130)
    print(json.dumps(res, indent=2))

if __name__ == "__main__":
    main()
