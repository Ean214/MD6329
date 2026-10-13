# -*- coding: utf-8 -*-
"""E5: in-silico closed-loop UF control trade-off (CORE deliverable).

Trains a dynamics model  P(IDH_post | pre-T state, planned_mean_uf_remaining,
remaining_min)  on CLINICIANS' ACTUAL post-T UF choices, then simulates three
control policies on the test set:
  1. constant   : keep actual clinician UF profile
  2. reactive   : rule-based proxy for biofeedback (drop early BP -> cut UF 30%)
  3. predictive : model chooses UF from candidate grid minimizing predicted
                  IDH risk subject to residual-fluid tolerance
Outputs per horizon T and tolerance: predicted IDH rate, residual fluid (mL),
required extension (min). ALL in-silico.

Usage: python e5_control.py [T ...]   (default 60 90 120)
"""
import json, os, sys
import numpy as np, pandas as pd
import xgboost as xgb

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import DATA, RESULTS, STAT_FEATS, SEED, save_json

EXTRA = ["planned_mean_uf_remaining", "remaining_min"]
TOLS_L = [0.25, 0.5, 1.0]          # residual fluid tolerance (litres)
GRID = [1.0, 0.9, 0.8, 0.7, 0.6]   # candidate multipliers of actual UF
MIN_UF = 0.1                          # L/h machine floor

def build(T):
    tab = pd.read_pickle(os.path.join(DATA, f"tabular_T{T}.pkl")).copy()
    tab = tab.rename(columns={"mean_uf_post": "planned_mean_uf_remaining"})
    # fluid accounting (litres)
    removed_pre = tab["mean_uf_so_far"] * (T / 60.0)          # L
    tab["remaining_target_L"] = (tab["idwg"] - removed_pre).clip(lower=0)
    tab["remaining_hours"] = tab["remaining_min"] / 60.0
    return tab

def train_dynamics(tab):
    feats = STAT_FEATS + EXTRA
    tr = tab[tab["split"] == "train"]
    scale = float((tr["y"] == 0).sum()) / max(1, int((tr["y"] == 1).sum()))
    clf = xgb.XGBClassifier(n_estimators=600, max_depth=6, learning_rate=0.05,
                            subsample=0.8, colsample_bytree=0.8, min_child_weight=5,
                            scale_pos_weight=scale, tree_method="hist",
                            random_state=SEED, n_jobs=8, eval_metric="aucpr")
    clf.fit(tr[feats].to_numpy(), tr["y"].to_numpy())
    return clf, feats

def simulate(tab, clf, feats, tol_L):
    te = tab[tab["split"] == "test"].copy()
    base_uf = te["planned_mean_uf_remaining"].clip(lower=MIN_UF).to_numpy()
    rem_h = te["remaining_hours"].to_numpy()
    target = te["remaining_target_L"].to_numpy()
    X = te[feats].to_numpy()

    def risk(uf):
        Xc = X.copy()
        Xc[:, feats.index("planned_mean_uf_remaining")] = uf
        return clf.predict_proba(Xc)[:, 1]

    def outcome(uf):
        resid = np.maximum(target - uf * rem_h, 0.0)              # L left in body
        ext = np.where(resid > 0, resid / np.maximum(uf, MIN_UF) * 60.0, 0.0)
        return resid * 1000.0, ext                                 # mL, min

    out = {}
    # 1. constant
    r = risk(base_uf); resid, ext = outcome(base_uf)
    out["constant"] = {"risk": float(r.mean()), "resid_mL": float(resid.mean()),
                       "ext_min": float(ext.mean())}
    # 2. reactive rule: early BP drop >=15 or nadir<100 -> cut 30%
    react = np.where((te["first_sbp"] - te["nadir_so_far"] >= 15) |
                     (te["nadir_so_far"] < 100), base_uf * 0.7, base_uf)
    react = np.maximum(react, MIN_UF)
    r = risk(react); resid, ext = outcome(react)
    out["reactive"] = {"risk": float(r.mean()), "resid_mL": float(resid.mean()),
                       "ext_min": float(ext.mean())}
    # 3. predictive: pick min risk subject to resid <= tol
    cand_risks = np.stack([risk(base_uf * g) for g in GRID], axis=1)   # [N, G]
    resid_c = np.stack([outcome(np.maximum(base_uf * g, MIN_UF))[0] / 1000.0
                        for g in GRID], axis=1)                        # L
    feas = resid_c <= tol_L
    feas_risk = np.where(feas, cand_risks, np.inf)
    any_feas = feas.any(axis=1)
    pick = np.where(any_feas, np.argmin(feas_risk, axis=1),
                    np.argmin(cand_risks, axis=1))
    uf_star = np.maximum(base_uf * np.array(GRID)[pick], MIN_UF)
    r = risk(uf_star); resid, ext = outcome(uf_star)
    out["predictive"] = {"risk": float(r.mean()), "resid_mL": float(resid.mean()),
                         "ext_min": float(ext.mean()),
                         "feasible_frac": float(any_feas.mean())}
    return out

def main():
    Ts = [int(x) for x in sys.argv[1:]] or [60, 90, 120]
    final = {}
    for T in Ts:
        tab = build(T)
        clf, feats = train_dynamics(tab)
        te = tab[tab["split"] == "test"]
        from sklearn.metrics import average_precision_score, roc_auc_score
        dyn = {"dynamics_auprc": round(float(average_precision_score(
                   te["y"], clf.predict_proba(te[feats].to_numpy())[:, 1])), 4),
               "dynamics_auroc": round(float(roc_auc_score(
                   te["y"], clf.predict_proba(te[feats].to_numpy())[:, 1])), 4)}
        res = {"horizon_T": T, "dynamics": dyn,
               "disclaimer": "ALL VALUES IN-SILICO under a dynamics model trained on clinicians' actual UF choices (confounded); not clinical validation."}
        for tol in TOLS_L:
            res[f"tol_{tol}L"] = simulate(tab, clf, feats, tol)
        final[f"T{T}"] = res
        print(json.dumps({f"T{T}": res}, ensure_ascii=False, indent=2), flush=True)
    save_json(final, "e5_tradeoff.json")

if __name__ == "__main__":
    main()
