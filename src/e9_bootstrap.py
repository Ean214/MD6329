# -*- coding: utf-8 -*-
"""
MD6329 Deep Learning for Healthcare AI -- final course project.
Generative AI assistance was used in writing this script, as disclosed in the
report (Section 4, "Software 3.0") and on the project cover page. The author
validated the implementation and the results, and remains responsible for both.

E9: (a) patient-level bootstrap confidence intervals for AUPRC, so that small
model differences are not over-read; (b) dataset attrition table.

Outputs results/e9_bootstrap.json, results/e9_attrition.json
"""
import json, os, sys
import numpy as np, pandas as pd
from sklearn.metrics import average_precision_score

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import DATA, RESULTS, save_json
from e8_calibration import get_probs

N_BOOT = 1000
T = 60

def bootstrap(probs, pid_test):
    uniq = np.unique(pid_test)
    idx_by_pid = {p: np.flatnonzero(pid_test == p) for p in uniq}
    rng = np.random.default_rng(42)
    names = list(probs.keys())
    store = {n: [] for n in names}
    store["transformer_minus_cnnmlp"] = []
    for _ in range(N_BOOT):
        pick = rng.choice(uniq, size=len(uniq), replace=True)
        idx = np.concatenate([idx_by_pid[p] for p in pick])
        for n in names:
            _, _, pt, yt = probs[n]
            store[n].append(average_precision_score(yt[idx], pt[idx]))
        store["transformer_minus_cnnmlp"].append(
            store["transformer"][-1] - store["cnnmlp"][-1])
    out = {}
    for n in names:
        arr = np.array(store[n])
        out[n] = {"auprc": round(float(average_precision_score(
            probs[n][3], probs[n][2])), 4),
            "ci95": [round(float(np.percentile(arr, 2.5)), 4),
                     round(float(np.percentile(arr, 97.5)), 4)]}
    d = np.array(store["transformer_minus_cnnmlp"])
    out["diff_transformer_minus_cnnmlp"] = {
        "point": round(out["transformer"]["auprc"] - out["cnnmlp"]["auprc"], 4),
        "ci95": [round(float(np.percentile(d, 2.5)), 4),
                 round(float(np.percentile(d, 97.5)), 4)],
        "prob_diff_gt_0": round(float((d > 0).mean()), 3)}
    return out

def attrition():
    sess = pd.read_csv(os.path.join(RESULTS, "sessions.csv"))
    steps = [["sessions reconstructed", len(sess)]]
    cur = sess
    for name, mask in [
        ("duration in [60, 480] min", (cur["duration_min"] >= 60) & (cur["duration_min"] <= 480)),
        ("start weight in [20, 200] kg", (cur["weightstart"] >= 20) & (cur["weightstart"] <= 200)),
        ("interdialytic gain in [-2, 10] kg", (cur["idwg"] >= -2) & (cur["idwg"] <= 10)),
        ("mean UFR in [0, 20] mL/kg/h", (cur["ufr_ml_kg_h"] >= 0) & (cur["ufr_ml_kg_h"] <= 20)),
    ]:
        cur = cur[mask]
        steps.append([name, len(cur)])
    steps.append(["eligible after cleaning", len(cur)])
    steps.append(["d1 weight record matched (82.7% of reconstructed)", int(sess["weightstart"].notna().sum())])
    out = {"steps": steps, "n_patients": int(cur["pid"].nunique())}
    for T in [30, 60, 90, 120]:
        n = int(len(np.load(os.path.join(DATA, f"seq_T{T}.npz"))["y"]))
        out[f"modelling_samples_T{T}"] = n
    out["note"] = ("Per-horizon drops beyond cleaning are: sessions shorter than T+30 min, "
                   "fewer than three readings before T, no readings after T, or already "
                   "below 90 mmHg before T.")
    return out

def main():
    probs = get_probs()
    d = np.load(os.path.join(DATA, f"seq_T{T}.npz"), allow_pickle=True)
    sp = d["split"]; pid = d["pid"]
    # get_probs uses tabular ordering, identical to seq ordering (same builder)
    pid_test = pid[sp == "test"]
    res = {"n_bootstrap": N_BOOT, "unit": "patient",
           "models": bootstrap(probs, pid_test)}
    save_json(res, "e9_bootstrap.json")
    print(json.dumps(res, indent=2))
    att = attrition()
    save_json(att, "e9_attrition.json")
    print(json.dumps(att, indent=2))

if __name__ == "__main__":
    main()
