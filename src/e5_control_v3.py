# -*- coding: utf-8 -*-
"""
MD6329 Deep Learning for Healthcare AI -- final course project.
Generative AI assistance was used in writing this script, as disclosed in the
report (Section 4, "Software 3.0") and on the project cover page. The author
validated the implementation and the results, and remains responsible for both.

E5 v3 -- exploratory, action-conditioned risk simulation.

Changes forced by the second review round:
  1. The anchor is now the UFR SETTING OBSERVED AT T (last non-zero pump setting
     at or before T), not the historical mean, so "hold the current rate" means
     what it says. The mean-so-far is retained as a fallback and reported.
  2. Overlap is reported CONDITIONALLY, not marginally: candidates are compared
     with observed post-T plans inside strata of (pre-T nadir SBP x IDWG).
  3. Policy metrics carry patient-level bootstrap intervals.
  4. A second, independently seeded dynamics model re-scores the chosen actions:
     if policy gains were driven by using one model to both choose and report,
     the two models should disagree.
  5. Everything is labelled exploratory; no arm is a validated policy.
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
N_BOOT = 500

def add_setting(T):
    """Attach the observed UFR setting at T (last non-zero value <= T)."""
    tab = pd.read_pickle(os.path.join(DATA, f"tabular_T{T}.pkl")).copy()
    d = np.load(os.path.join(DATA, f"seq_T{T}.npz"))
    X, M = d["X_seq"], d["mask"]
    uf = X[:, :, 2] * M                      # zero at pads
    # last non-zero position
    nz = uf > 0
    last = np.where(nz.any(1), uf.shape[1] - 1 - np.argmax(nz[:, ::-1], axis=1), -1)
    uf_set = np.where(last >= 0, uf[np.arange(len(uf)), np.clip(last, 0, uf.shape[1]-1)], np.nan)
    assert len(uf_set) == len(tab), "row-order mismatch between npz and pickle"
    tab["uf_set_at_T"] = uf_set
    tab = tab.rename(columns={"mean_uf_post": "planned_uf"})
    removed_pre = tab["mean_uf_so_far"] * (T / 60.0)
    tab["remaining_target_L"] = (tab["idwg"] - removed_pre).clip(lower=0)
    tab["remaining_hours"] = tab["remaining_min"] / 60.0
    tab["anchor_uf"] = tab["uf_set_at_T"].fillna(tab["mean_uf_so_far"]).clip(lower=MIN_UF)
    return tab

def fit(tab, depth=6, seed=SEED, use_weight=True):
    feats = STAT_FEATS + EXTRA
    tr = tab[tab["split"] == "train"]
    scale = float((tr["y"] == 0).sum()) / max(1, int((tr["y"] == 1).sum())) if use_weight else 1.0
    clf = xgb.XGBClassifier(n_estimators=600, max_depth=depth, learning_rate=0.05,
                            subsample=0.8, colsample_bytree=0.8, min_child_weight=5,
                            scale_pos_weight=scale, tree_method="hist",
                            random_state=seed, n_jobs=8, eval_metric="aucpr")
    clf.fit(tr[feats].to_numpy(), tr["y"].to_numpy())
    va = tab[tab["split"] == "val"]
    p = clf.predict_proba(va[feats].to_numpy())[:, 1]
    eps = 1e-6
    lg = np.log(np.clip(p, eps, 1-eps) / np.clip(1-p, eps, 1-eps)).reshape(-1, 1)
    platt = LogisticRegression(C=1e6, solver="lbfgs").fit(lg, va["y"].to_numpy())
    return clf, platt, feats

def calibrated(clf, platt, feats, X, uf_idx, uf):
    Xc = X.copy(); Xc[:, uf_idx] = uf
    p = clf.predict_proba(Xc)[:, 1]
    eps = 1e-6
    lg = np.log(np.clip(p, eps, 1-eps) / np.clip(1-p, eps, 1-eps)).reshape(-1, 1)
    return platt.predict_proba(lg)[:, 1]

def overlap(tab):
    tr = tab[(tab["split"] == "train") & (tab["planned_uf"] > 0)]
    te = tab[tab["split"] == "test"]
    lo, hi = np.percentile(tr["planned_uf"], [5, 95])
    cand = np.stack([np.maximum(te["anchor_uf"].to_numpy() * g, MIN_UF) for g in GRID], 1)
    marginal = float(((cand >= lo) & (cand <= hi)).mean())
    # conditional: stratum = (nadir_so_far quintile, idwg quintile)
    tr = tr.copy()
    tr["q_nadir"] = pd.qcut(tr["nadir_so_far"], 5, labels=False, duplicates="drop")
    tr["q_idwg"] = pd.qcut(tr["idwg"], 5, labels=False, duplicates="drop")
    te = te.copy()
    te["q_nadir"] = pd.cut(te["nadir_so_far"],
                           bins=np.unique(np.percentile(tr["nadir_so_far"], [0,20,40,60,80,100])),
                           labels=False, include_lowest=True)
    te["q_idwg"] = pd.cut(te["idwg"],
                          bins=np.unique(np.percentile(tr["idwg"], [0,20,40,60,80,100])),
                          labels=False, include_lowest=True)
    inside, total, strata_used = 0, 0, 0
    for (qn, qi), grp in te.groupby(["q_nadir", "q_idwg"]):
        ref = tr[(tr["q_nadir"] == qn) & (tr["q_idwg"] == qi)]
        if len(ref) < 30:
            continue
        strata_used += 1
        l, h = np.percentile(ref["planned_uf"], [10, 90])
        c = np.stack([np.maximum(grp["anchor_uf"].to_numpy() * g, MIN_UF) for g in GRID], 1)
        inside += int(((c >= l) & (c <= h)).sum()); total += c.size
    return {"support_p5_p95": [round(float(lo), 3), round(float(hi), 3)],
            "marginal_inside": round(marginal, 3),
            "conditional_inside": round(inside / max(total, 1), 3),
            "strata_used": strata_used,
            "note": "conditional = candidates inside the 10-90 percentile of observed post-T plans within a (nadir SBP x IDWG) quintile stratum"}

def policy_arrays(tab, clf, platt, feats):
    te = tab[tab["split"] == "test"]
    X = te[feats].to_numpy(); ui = feats.index("planned_uf")
    anchor = te["anchor_uf"].to_numpy()
    rem_h = te["remaining_hours"].to_numpy(); target = te["remaining_target_L"].to_numpy()
    def out(uf):
        resid = np.maximum(target - uf * rem_h, 0.0)
        ext = np.where(resid > 0, resid / np.maximum(uf, MIN_UF) * 60.0, 0.0)
        return resid * 1000.0, ext
    res = {}
    uf_obs = te["planned_uf"].clip(lower=MIN_UF).to_numpy()
    res["reference"] = dict(uf=uf_obs, risk=calibrated(clf, platt, feats, X, ui, uf_obs), *out(uf_obs)[:0]) if False else None
    def pack(uf):
        r = calibrated(clf, platt, feats, X, ui, uf)
        resid, ext = out(uf)
        return {"uf": uf, "risk": r, "resid": resid, "ext": ext}
    arms = {"reference_observed_plan": pack(uf_obs), "hold": pack(anchor)}
    trig = (te["first_sbp"] - te["nadir_so_far"] >= 15) | (te["nadir_so_far"] < 100)
    arms["reactive"] = pack(np.maximum(np.where(trig, anchor * 0.7, anchor), MIN_UF))
    # predictive under 0.5 L tolerance (the reported arm) + other tolerances
    for tol in TOLS_L:
        cr = np.stack([pack(np.maximum(anchor * g, MIN_UF))["risk"] for g in GRID], 1)
        rc = np.stack([pack(np.maximum(anchor * g, MIN_UF))["resid"] for g in GRID], 1) / 1000.0
        feas = rc <= tol
        pick = np.where(feas.any(1), np.argmin(np.where(feas, cr, np.inf), axis=1), np.argmin(cr, axis=1))
        arms[f"predictive_tol{tol}"] = pack(np.maximum(anchor * np.array(GRID)[pick], MIN_UF))
    return te, arms

def boot_ci(arr, pid, n=N_BOOT):
    uniq = np.unique(pid)
    idx = {p: np.flatnonzero(pid == p) for p in uniq}
    rng = np.random.default_rng(42)
    vals = []
    for _ in range(n):
        pick = rng.choice(uniq, len(uniq), replace=True)
        s = np.concatenate([idx[p] for p in pick])
        vals.append(arr[s].mean())
    return [round(float(np.percentile(vals, 2.5)), 4), round(float(np.percentile(vals, 97.5)), 4)]

def main():
    T = 60
    tab = add_setting(T)
    clf, platt, feats = fit(tab)
    te, arms = policy_arrays(tab, clf, platt, feats)
    pid = te["pid"].to_numpy()
    p_raw = clf.predict_proba(te[feats].to_numpy())[:, 1]
    summary = {"horizon_T": T, "n_test": int(len(te)),
               "label": "exploratory action-conditioned risk simulation (NOT policy validation)",
               "anchor_definition": "UFR setting observed at T (last non-zero pump value <= T); mean-so-far as fallback",
               "anchor_check": {"mean_uf_set_at_T": round(float(tab["uf_set_at_T"].mean()), 3),
                                "mean_uf_so_far": round(float(tab["mean_uf_so_far"].mean()), 3),
                                "corr": round(float(tab["uf_set_at_T"].corr(tab["mean_uf_so_far"])), 3)},
               "dynamics": {"auprc": round(float(average_precision_score(te["y"], p_raw)), 4),
                            "auroc": round(float(roc_auc_score(te["y"], p_raw)), 4),
                            "observed": round(float(te["y"].mean()), 4)},
               "overlap": overlap(tab)}
    for name, a in arms.items():
        summary[name] = {"risk": round(float(a["risk"].mean()), 4),
                         "risk_ci95": boot_ci(a["risk"], pid),
                         "resid_mL": round(float(a["resid"].mean()), 1),
                         "resid_ci95": boot_ci(a["resid"], pid),
                         "ext_min": round(float(a["ext"].mean()), 1),
                         "mean_uf": round(float(a["uf"].mean()), 3)}
    # cross-model check: does a second, independently seeded model agree on the chosen actions?
    clf2, platt2, _ = fit(tab, depth=3, seed=7, use_weight=False)
    X = te[feats].to_numpy(); ui = feats.index("planned_uf")
    for key in ["hold", "reactive", "predictive_tol0.5"]:
        r2 = calibrated(clf2, platt2, feats, X, ui, arms[key]["uf"])
        summary[key]["risk_model2"] = round(float(r2.mean()), 4)
        summary[key]["model_agreement_corr"] = round(float(np.corrcoef(arms[key]["risk"], r2)[0, 1]), 3)
    save_json(summary, "e5_tradeoff_v3.json")
    print(json.dumps(summary, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
