# -*- coding: utf-8 -*-
"""
MD6329 Deep Learning for Healthcare AI -- final course project.
Generative AI assistance was used in writing this script, as disclosed in the
report (Section 4, "Software 3.0") and on the project cover page. The author
validated the implementation and the results, and remains responsible for both.

E5 (revised after review): in-silico closed-loop UF control trade-off.

What changed and why
--------------------
The first version anchored the candidate actions on the mean UF that was
*actually delivered after T*. That value does not exist at decision time, so the
simulated policy could not be executed. Candidates are now generated only from
information available at T:

    anchor = mean UF delivered so far (observed at T)

and the dynamics model is asked to score a *candidate plan* supplied by the
policy. The model is trained on (state at T, observed post-T mean UF) -> IDH, so
it is a CONDITIONAL RISK model, not an identified counterfactual model. We
therefore also report an overlap diagnostic: how far the candidate plans sit from
what clinicians actually did. Predictions outside that support are
extrapolations, not estimates.

Probabilities are Platt-recalibrated on validation before any risk is quoted:
the raw scores over-predict by 4-6x (see E8).

Usage: python e5_control.py [T ...]
"""
import json, os, sys
import numpy as np, pandas as pd
import xgboost as xgb
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, roc_auc_score

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import DATA, RESULTS, STAT_FEATS, SEED, save_json

EXTRA = ["planned_uf", "remaining_min"]
TOLS_L = [0.25, 0.5, 1.0]
GRID = [1.0, 0.9, 0.8, 0.7, 0.6]
MIN_UF = 0.1

def build(T):
    tab = pd.read_pickle(os.path.join(DATA, f"tabular_T{T}.pkl")).copy()
    # observed post-T mean UF: used ONLY to condition the training target
    tab = tab.rename(columns={"mean_uf_post": "planned_uf"})
    removed_pre = tab["mean_uf_so_far"] * (T / 60.0)
    tab["remaining_target_L"] = (tab["idwg"] - removed_pre).clip(lower=0)
    tab["remaining_hours"] = tab["remaining_min"] / 60.0
    tab["anchor_uf"] = tab["mean_uf_so_far"].clip(lower=MIN_UF)   # decision-time
    return tab

def fit_dynamics(tab):
    feats = STAT_FEATS + EXTRA
    tr = tab[tab["split"] == "train"]
    scale = float((tr["y"] == 0).sum()) / max(1, int((tr["y"] == 1).sum()))
    clf = xgb.XGBClassifier(n_estimators=600, max_depth=6, learning_rate=0.05,
                            subsample=0.8, colsample_bytree=0.8, min_child_weight=5,
                            scale_pos_weight=scale, tree_method="hist",
                            random_state=SEED, n_jobs=8, eval_metric="aucpr")
    clf.fit(tr[feats].to_numpy(), tr["y"].to_numpy())
    return clf, feats

def fit_platt(clf, feats, tab):
    va = tab[tab["split"] == "val"]
    p = clf.predict_proba(va[feats].to_numpy())[:, 1]
    eps = 1e-6
    lg = np.log(np.clip(p, eps, 1 - eps) / np.clip(1 - p, eps, 1 - eps)).reshape(-1, 1)
    lr = LogisticRegression(C=1e6, solver="lbfgs").fit(lg, va["y"].to_numpy())
    return lr

def apply_platt(lr, p):
    eps = 1e-6
    lg = np.log(np.clip(p, eps, 1 - eps) / np.clip(1 - p, eps, 1 - eps)).reshape(-1, 1)
    return lr.predict_proba(lg)[:, 1]

def overlap(tab, tol_q=(5, 95)):
    """Fraction of candidate plans inside the observed post-T UF support."""
    tr = tab[(tab["split"] == "train") & (tab["planned_uf"] > 0)]
    lo, hi = np.percentile(tr["planned_uf"], tol_q)
    te = tab[tab["split"] == "test"]
    cand = np.stack([np.maximum(te["anchor_uf"].to_numpy() * g, MIN_UF) for g in GRID], axis=1)
    inside = ((cand >= lo) & (cand <= hi)).mean()
    dev = np.abs(cand - te["planned_uf"].to_numpy()[:, None]).mean()
    return {"support_lo": round(float(lo), 3), "support_hi": round(float(hi), 3),
            "frac_candidates_inside_support": round(float(inside), 3),
            "mean_abs_deviation_from_observed_plan_L_h": round(float(dev), 3)}

def simulate(tab, clf, feats, platt, tol_L):
    te = tab[tab["split"] == "test"]
    X = te[feats].to_numpy()
    anchor = te["anchor_uf"].to_numpy()
    rem_h = te["remaining_hours"].to_numpy()
    target = te["remaining_target_L"].to_numpy()
    uf_idx = feats.index("planned_uf")

    def risk(uf):
        Xc = X.copy(); Xc[:, uf_idx] = uf
        return apply_platt(platt, clf.predict_proba(Xc)[:, 1])

    def outcome(uf):
        resid = np.maximum(target - uf * rem_h, 0.0)
        ext = np.where(resid > 0, resid / np.maximum(uf, MIN_UF) * 60.0, 0.0)
        return resid * 1000.0, ext

    out = {}
    # descriptive reference only: what clinicians actually did after T.
    # NOT a policy arm, because it is not a choice available at T.
    uf_obs = te["planned_uf"].clip(lower=MIN_UF).to_numpy()
    r = risk(uf_obs); resid, ext = outcome(uf_obs)
    out["reference_observed_plan"] = {"risk": float(r.mean()), "resid_mL": float(resid.mean()),
                                      "ext_min": float(ext.mean()),
                                      "mean_uf": float(uf_obs.mean())}
    # arm 1: hold the rate observed at decision time
    r = risk(anchor); resid, ext = outcome(anchor)
    out["hold"] = {"risk": float(r.mean()), "resid_mL": float(resid.mean()),
                   "ext_min": float(ext.mean())}
    react = np.where((te["first_sbp"] - te["nadir_so_far"] >= 15) |
                     (te["nadir_so_far"] < 100), anchor * 0.7, anchor)
    react = np.maximum(react, MIN_UF)
    r = risk(react); resid, ext = outcome(react)
    out["reactive"] = {"risk": float(r.mean()), "resid_mL": float(resid.mean()),
                       "ext_min": float(ext.mean()),
                       "triggered_frac": float(((te["first_sbp"] - te["nadir_so_far"] >= 15) |
                                                (te["nadir_so_far"] < 100)).mean())}
    cr = np.stack([risk(np.maximum(anchor * g, MIN_UF)) for g in GRID], axis=1)
    resid_c = np.stack([outcome(np.maximum(anchor * g, MIN_UF))[0] / 1000.0 for g in GRID], axis=1)
    feas = resid_c <= tol_L
    pick = np.where(feas.any(1), np.argmin(np.where(feas, cr, np.inf), axis=1), np.argmin(cr, axis=1))
    uf_star = np.maximum(anchor * np.array(GRID)[pick], MIN_UF)
    r = risk(uf_star); resid, ext = outcome(uf_star)
    out["predictive"] = {"risk": float(r.mean()), "resid_mL": float(resid.mean()),
                         "ext_min": float(ext.mean()), "feasible_frac": float(feas.any(1).mean()),
                         "mean_chosen_multiplier": float(np.array(GRID)[pick].mean())}
    return out

def main():
    Ts = [int(x) for x in sys.argv[1:]] or [60, 90, 120]
    final = {}
    for T in Ts:
        tab = build(T)
        clf, feats = fit_dynamics(tab)
        platt = fit_platt(clf, feats, tab)
        te = tab[tab["split"] == "test"]
        p_raw = clf.predict_proba(te[feats].to_numpy())[:, 1]
        res = {"horizon_T": T,
               "dynamics": {"auprc": round(float(average_precision_score(te["y"], p_raw)), 4),
                            "auroc": round(float(roc_auc_score(te["y"], p_raw)), 4),
                            "mean_pred_raw": round(float(p_raw.mean()), 4),
                            "mean_pred_calibrated": round(float(apply_platt(platt, p_raw).mean()), 4),
                            "observed": round(float(te["y"].mean()), 4)},
               "overlap": overlap(tab),
               "candidate_anchor": "mean UF delivered up to T (decision-time observable)",
               "disclaimer": ("IN-SILICO. The dynamics model is a conditional-risk model "
                              "trained on clinicians' observed plans; treating it as a "
                              "counterfactual model is an extrapolation whose support is "
                              "quantified by the overlap diagnostic.")}
        for tol in TOLS_L:
            res[f"tol_{tol}L"] = simulate(tab, clf, feats, platt, tol)
        final[f"T{T}"] = res
        print(json.dumps({f"T{T}": res}, ensure_ascii=False, indent=2), flush=True)
    save_json(final, "e5_tradeoff_v2.json")

if __name__ == "__main__":
    main()
