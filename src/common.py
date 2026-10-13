# -*- coding: utf-8 -*-
"""Shared utilities: seed, patient-group split, metrics."""
import json, os, numpy as np, pandas as pd

SEED = 42
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS = os.path.join(BASE, "results")
DATA = os.path.join(BASE, "data")

STAT_FEATS = ["T_min", "age", "gender_m", "DM", "weightstart", "dryweight", "idwg",
              "first_sbp", "nadir_so_far", "slope_sbp", "mean_uf_so_far",
              "mean_bf_so_far", "mean_cond_so_far", "mean_temp_so_far", "n_bp_so_far"]

def rng():
    return np.random.default_rng(SEED)

def patient_split(sessions_csv=None, train=0.70, val=0.15, test=0.15):
    """Group split by pid. Returns dict pid->split. Stratifies roughly by
    patient-level IDH rate so test prevalence ~ overall."""
    sess = pd.read_csv(sessions_csv or os.path.join(RESULTS, "sessions.csv"),
                       usecols=["pid", "idh_nadir90"])
    rate = sess.groupby("pid")["idh_nadir90"].mean().sort_values()
    pids = rate.index.to_numpy().copy()
    r = rng()
    r.shuffle(pids)
    n = len(pids)
    n_tr, n_va = int(n * train), int(n * (train + val))
    split = {}
    for i, p in enumerate(pids):
        split[int(p)] = "train" if i < n_tr else ("val" if i < n_va else "test")
    return split

def metrics(y_true, y_prob):
    from sklearn.metrics import (average_precision_score, roc_auc_score,
                                 brier_score_loss, recall_score)
    y_true = np.asarray(y_true).astype(int)
    y_prob = np.asarray(y_prob, dtype=float)
    out = {}
    out["n"] = int(len(y_true))
    out["prevalence"] = round(float(y_true.mean()), 4)
    out["auprc"] = round(float(average_precision_score(y_true, y_prob)), 4)
    out["auroc"] = round(float(roc_auc_score(y_true, y_prob)), 4)
    out["brier"] = round(float(brier_score_loss(y_true, y_prob)), 4)
    # sensitivity at specificity ~0.8: among ROC points meeting spec>=0.8,
    # take the one with max TPR (i.e., the operating point just inside the spec bound)
    from sklearn.metrics import roc_curve
    fpr, tpr, thr = roc_curve(y_true, y_prob)
    spec = 1 - fpr
    cand = np.flatnonzero(spec >= 0.8)
    out["sens_at_spec0.8"] = round(float(tpr[cand].max()), 4) if len(cand) else 0.0
    return out

def save_json(obj, name):
    os.makedirs(RESULTS, exist_ok=True)
    path = os.path.join(RESULTS, name)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2, default=str)
    print("saved", path)
