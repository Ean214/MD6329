# -*- coding: utf-8 -*-
"""
MD6329 Deep Learning for Healthcare AI -- final course project.
Generative AI assistance was used in writing this script, as disclosed in the
report (Section 4, "Software 3.0") and on the project cover page. The author
validated the implementation and the results, and remains responsible for both.
"""
"""D1-XGBoost: tabular baseline for IDH prediction (E1 arm 1).
Usage: python d1_xgboost.py [T]   (default T=60)
"""
import json, os, sys, time
import numpy as np, pandas as pd
import xgboost as xgb

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import BASE, DATA, RESULTS, STAT_FEATS, metrics, save_json, SEED

T = int(sys.argv[1]) if len(sys.argv) > 1 else 60

def main():
    tab = pd.read_pickle(os.path.join(DATA, f"tabular_T{T}.pkl"))
    feats = STAT_FEATS
    tr = tab[tab["split"] == "train"]; te = tab[tab["split"] == "test"]
    Xtr, ytr = tr[feats].to_numpy(), tr["y"].to_numpy()
    Xte, yte = te[feats].to_numpy(), te["y"].to_numpy()
    scale = float((ytr == 0).sum()) / max(1, int((ytr == 1).sum()))
    clf = xgb.XGBClassifier(
        n_estimators=600, max_depth=6, learning_rate=0.05,
        subsample=0.8, colsample_bytree=0.8, min_child_weight=5,
        scale_pos_weight=scale, tree_method="hist",
        random_state=SEED, n_jobs=8, eval_metric="aucpr")
    t0 = time.time()
    clf.fit(Xtr, ytr)
    prob = clf.predict_proba(Xte)[:, 1]
    res = metrics(yte, prob)
    res["model"] = "xgboost"; res["horizon_T"] = T
    res["train_time_s"] = round(time.time() - t0, 1)
    res["n_train"] = int(len(tr)); res["n_test"] = int(len(te))
    imp = sorted(zip(feats, clf.feature_importances_.tolist()),
                 key=lambda x: -x[1])[:8]
    res["top_features"] = [(k, round(float(v), 4)) for k, v in imp]
    save_json(res, f"e1_xgboost_T{T}.json")
    print(json.dumps(res, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
