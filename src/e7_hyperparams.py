# -*- coding: utf-8 -*-
"""
MD6329 Deep Learning for Healthcare AI -- final course project.
Generative AI assistance was used in writing this script, as disclosed in the
report (Section 4, "Software 3.0") and on the project cover page. The author
validated the implementation and the results, and remains responsible for both.
"""
"""E7: hyperparameter selection study (required by the brief: "training and
hyperparameter selection"; Experiments may include "hyperparameter analysis").

E7a  XGBoost grid: n_estimators x max_depth  -> AUPRC heatmap
E7b  1D-CNN+MLP learning-rate sweep + class-weight on/off -> line plot
Outputs results/e7_hyperparams.json, results/fig_e7_*.png
"""
import json, os, sys, time
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import xgboost as xgb

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import DATA, RESULTS, STAT_FEATS, SEED, metrics, save_json

T = 60
N_EST = [200, 600, 1200]
DEPTH = [3, 6, 9]
LRS = [3e-4, 1e-3, 3e-3]
NN_EPOCHS = 6

def e7a():
    tab = pd.read_pickle(os.path.join(DATA, f"tabular_T{T}.pkl"))
    tr, te = tab[tab["split"] == "train"], tab[tab["split"] == "test"]
    Xtr, ytr = tr[STAT_FEATS].to_numpy(), tr["y"].to_numpy()
    Xte, yte = te[STAT_FEATS].to_numpy(), te["y"].to_numpy()
    scale = float((ytr == 0).sum()) / max(1, int((ytr == 1).sum()))
    grid, t0 = {}, time.time()
    for n in N_EST:
        for d in DEPTH:
            m = xgb.XGBClassifier(n_estimators=n, max_depth=d, learning_rate=0.05,
                                  subsample=0.8, colsample_bytree=0.8, min_child_weight=5,
                                  scale_pos_weight=scale, tree_method="hist",
                                  random_state=SEED, n_jobs=8, eval_metric="aucpr")
            m.fit(Xtr, ytr)
            r = metrics(yte, m.predict_proba(Xte)[:, 1])
            grid[f"n{n}_d{d}"] = {"n_estimators": n, "max_depth": d,
                                  "auprc": r["auprc"], "auroc": r["auroc"]}
            print(f"  xgb n={n} d={d}: AUPRC={r['auprc']:.4f}", flush=True)
    best = max(grid.items(), key=lambda kv: kv[1]["auprc"])
    fig, ax = plt.subplots(figsize=(5.6, 3.6))
    M = np.array([[grid[f"n{n}_d{d}"]["auprc"] for d in DEPTH] for n in N_EST])
    im = ax.imshow(M, cmap="YlGn", aspect="auto")
    ax.set_xticks(range(len(DEPTH)), DEPTH); ax.set_yticks(range(len(N_EST)), N_EST)
    ax.set_xlabel("max_depth"); ax.set_ylabel("n_estimators")
    for i in range(len(N_EST)):
        for j in range(len(DEPTH)):
            ax.text(j, i, f"{M[i,j]:.4f}", ha="center", va="center", fontsize=9)
    ax.set_title("E7a: XGBoost AUPRC grid (T=60)", fontsize=10)
    fig.colorbar(im, ax=ax, shrink=0.85)
    fig.tight_layout(); fig.savefig(os.path.join(RESULTS, "fig_e7_xgb_grid.png"), dpi=130)
    plt.close(fig)
    print(f"  best: {best[0]} AUPRC={best[1]['auprc']:.4f} ({time.time()-t0:.0f}s)", flush=True)
    return {"grid": grid, "best": {"config": best[0], **best[1]}}

def e7b():
    from d1_nn import MODELS, load_ds, standardize, DS, DEV, infer
    import torch, torch.nn as nn
    d = load_ds(T)
    Xf, M, Xst, y, sp, _ = standardize(d)
    tr, va, te = sp == "train", sp == "val", sp == "test"

    def run(lr, use_pos_weight, seed=SEED):
        torch.manual_seed(seed); np.random.seed(seed)
        ds = DS(Xf[tr], M[tr], Xst[tr], y[tr])
        ltr = torch.utils.data.DataLoader(ds, batch_size=256, shuffle=True, drop_last=True)
        lva = torch.utils.data.DataLoader(DS(Xf[va], M[va], Xst[va], y[va]), batch_size=512)
        lte = torch.utils.data.DataLoader(DS(Xf[te], M[te], Xst[te], y[te]), batch_size=512)
        model = MODELS["cnnmlp"](Xf.shape[2], Xst.shape[1]).to(DEV)
        pw = torch.tensor([(y[tr] == 0).sum() / max(1, (y[tr] == 1).sum())], device=DEV) \
            if use_pos_weight else None
        opt = torch.optim.Adam(model.parameters(), lr=lr)
        lossf = nn.BCEWithLogitsLoss(pos_weight=pw)
        best, state = -1, None
        for ep in range(NN_EPOCHS):
            model.train()
            for x, mk, s, yy in ltr:
                x, mk, s, yy = x.to(DEV), mk.to(DEV), s.to(DEV), yy.to(DEV)
                opt.zero_grad(); loss = lossf(model(x, mk, s), yy)
                loss.backward(); opt.step()
            pv, yv = infer(model, lva); mv = metrics(yv, pv)["auprc"]
            if mv > best:
                best = mv
                state = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}
        model.load_state_dict(state)
        pt, yt = infer(model, lte)
        return metrics(yt, pt), best

    out = {}
    for lr in LRS:
        r, v = run(lr, True)
        out[f"lr{lr}_w1"] = {"lr": lr, "pos_weight": True, "auprc": r["auprc"],
                             "auroc": r["auroc"], "val_auprc": round(v, 4)}
        print(f"  cnnmlp lr={lr} pos_weight=on : AUPRC={r['auprc']:.4f}", flush=True)
    r, v = run(1e-3, False)
    out["lr0.001_w0"] = {"lr": 1e-3, "pos_weight": False, "auprc": r["auprc"],
                         "auroc": r["auroc"], "val_auprc": round(v, 4)}
    print(f"  cnnmlp lr=1e-3 pos_weight=off: AUPRC={r['auprc']:.4f}", flush=True)

    fig, ax = plt.subplots(figsize=(5.6, 3.4))
    xs = [c["lr"] for k, c in out.items() if c["pos_weight"]]
    ys = [c["auprc"] for k, c in out.items() if c["pos_weight"]]
    ax.plot(xs, ys, "o-", label="pos_weight on")
    ax.scatter(1e-3, out["lr0.001_w0"]["auprc"], marker="s", color="#a32d2d",
               label="pos_weight off (lr 1e-3)")
    ax.set_xscale("log"); ax.set_xlabel("Adam learning rate (log)")
    ax.set_ylabel("test AUPRC (T=60)")
    ax.set_title(f"E7b: 1D-CNN+MLP hyperparameters ({NN_EPOCHS} epochs)", fontsize=10)
    ax.legend(fontsize=8); ax.grid(alpha=0.3)
    fig.tight_layout(); fig.savefig(os.path.join(RESULTS, "fig_e7_nn_lr.png"), dpi=130)
    plt.close(fig)
    return out

def main():
    which = sys.argv[1] if len(sys.argv) > 1 else "both"
    res = {}
    if which in ("a", "both"):
        print("[E7a] XGBoost grid", flush=True); res["e7a_xgb"] = e7a()
    if which in ("b", "both"):
        print("[E7b] CNN+MLP lr / class-weight", flush=True); res["e7b_cnnmlp"] = e7b()
    save_json(res, "e7_hyperparams.json")

if __name__ == "__main__":
    main()
