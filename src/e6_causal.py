# -*- coding: utf-8 -*-
"""
MD6329 Deep Learning for Healthcare AI -- final course project.
Generative AI assistance was used in writing this script, as disclosed in the
report (Section 4, "Software 3.0") and on the project cover page. The author
validated the implementation and the results, and remains responsible for both.
"""
"""E6: causal diagnosis (confounding-by-indication exposure).

Two analyses on the dynamics model (E5):
  A) UF perturbation sweep: predicted IDH risk vs planned remaining UF
     multiplier. Reverse gradient (higher UF -> lower predicted risk) is the
     signature of confounding by indication.
  B) Crude empirical association: binned actual post-T UF vs observed IDH rate.
Produces results/e6_*.json + results/fig_e6_*.png.
"""
import json, os, sys
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import xgboost as xgb

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import DATA, RESULTS, STAT_FEATS, SEED, save_json
from e5_control import build, train_dynamics, EXTRA

MULTS = np.round(np.arange(0.3, 1.31, 0.1), 2)

def main():
    T = int(sys.argv[1]) if len(sys.argv) > 1 else 60
    tab = build(T)
    clf, feats = train_dynamics(tab)
    te = tab[tab["split"] == "test"].copy()
    X = te[feats].to_numpy()
    uf_idx = feats.index("planned_mean_uf_remaining")
    base = te["planned_mean_uf_remaining"].clip(lower=0.1).to_numpy()

    risks = []
    for m in MULTS:
        Xc = X.copy()
        Xc[:, uf_idx] = np.maximum(base * m, 0.1)
        risks.append(float(clf.predict_proba(Xc)[:, 1].mean()))
    grad = np.polyfit(MULTS, risks, 1)[0]
    res_perturb = {"T": T, "mults": MULTS.tolist(), "mean_risk": risks,
                   "gradient": float(grad),
                   "interpretation": ("positive gradient: model thinks higher UF "
                                      "raises risk (expected); near-zero/negative "
                                      "gradient => confounded signal dominant")}
    save_json(res_perturb, f"e6_perturb_T{T}.json")
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(MULTS, risks, "o-")
    ax.axvline(1.0, color="gray", ls="--")
    ax.set_xlabel("remaining UF multiplier (1.0 = clinician actual)")
    ax.set_ylabel("mean predicted P(IDH)")
    ax.set_title(f"E6-A UF perturbation (T={T}), grad={grad:.3f}")
    fig.tight_layout(); fig.savefig(os.path.join(RESULTS, f"fig_e6_perturb_T{T}.png"), dpi=120)
    plt.close(fig)

    # B) crude empirical association
    te2 = te.dropna(subset=["planned_mean_uf_remaining"]).copy()
    te2["uf_bin"] = pd.qcut(te2["planned_mean_uf_remaining"], 8, duplicates="drop")
    emp = te2.groupby("uf_bin", observed=True).agg(
        uf_mean=("planned_mean_uf_remaining", "mean"),
        idh_rate=("y", "mean"), n=("y", "size")).reset_index(drop=True)
    save_json({"T": T, "binned": emp.round(4).to_dict("records")}, f"e6_empirical_T{T}.json")
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(emp["uf_mean"], emp["idh_rate"], "o-")
    ax.set_xlabel("actual post-T UF (L/h, binned mean)")
    ax.set_ylabel("observed IDH rate")
    ax.set_title(f"E6-B crude UF-IDH association (T={T})")
    fig.tight_layout(); fig.savefig(os.path.join(RESULTS, f"fig_e6_empirical_T{T}.png"), dpi=120)
    plt.close(fig)
    print(json.dumps({"perturb_gradient": res_perturb["gradient"],
                      "empirical": emp.round(4).to_dict("records")}, indent=2))

if __name__ == "__main__":
    main()
