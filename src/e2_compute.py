# -*- coding: utf-8 -*-
"""E2: compute budget (params / FLOPs / latency) for Edge-AI argument (C2).
Outputs results/e2_compute.json + results/fig_e2_pareto.png
"""
import json, os, sys, time
import numpy as np, torch
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import DATA, RESULTS, STAT_FEATS, save_json
from d1_nn import MODELS, load_ds, standardize

T = 60

def flops_of(model, fin, sdim, L=96):
    try:
        from torch.utils.flop_counter import FlopCounterMode
        x = torch.randn(1, L, fin); m = torch.ones(1, L); s = torch.randn(1, sdim)
        with FlopCounterMode(display=False) as fc:
            model(x, m, s)
        return int(sum(fc.get_total_flops().values())) if hasattr(fc.get_total_flops(), "values") else int(fc.get_total_flops())
    except Exception as e:
        return None

def latency(model, fin, sdim, L=96, n=50, bs=1, dev="cpu"):
    model = model.to(dev).eval()
    x = torch.randn(bs, L, fin, device=dev); m = torch.ones(bs, L, device=dev)
    s = torch.randn(bs, sdim, device=dev)
    with torch.no_grad():
        for _ in range(5): model(x, m, s)
        if dev == "cuda": torch.cuda.synchronize()
        t0 = time.perf_counter()
        for _ in range(n): model(x, m, s)
        if dev == "cuda": torch.cuda.synchronize()
        return (time.perf_counter() - t0) / n * 1000.0  # ms

def main():
    d = load_ds(T)
    fin, sdim = d["X_seq"].shape[2], d["X_stat"].shape[1]
    out = {}
    for name in ["mlp", "cnnmlp", "lstm", "transformer"]:
        model = MODELS[name](fin, sdim)
        ck = os.path.join(RESULTS, f"ckpt_{name}_T{T}.pt")
        if os.path.exists(ck):
            model.load_state_dict(torch.load(ck, map_location="cpu"))
        e1 = json.load(open(os.path.join(RESULTS, f"e1_{name}_T{T}.json")))
        out[name] = {
            "params": int(sum(p.numel() for p in model.parameters())),
            "flops_per_sample": flops_of(model, fin, sdim),
            "latency_ms_cpu_bs1": round(latency(model, fin, sdim, dev="cpu"), 3),
            "latency_ms_cpu_bs256": round(latency(model, fin, sdim, n=20, bs=256, dev="cpu"), 3),
            "auprc": e1["auprc"], "auroc": e1["auroc"],
        }
        if torch.cuda.is_available():
            out[name]["latency_ms_gpu_bs1"] = round(latency(model, fin, sdim, dev="cuda"), 3)
    # XGBoost: tree count as size proxy + cpu latency
    import xgboost as xgb, pandas as pd
    tab = pd.read_pickle(os.path.join(DATA, f"tabular_T{T}.pkl"))
    tab = pd.read_pickle(os.path.join(DATA, f"tabular_T{T}.pkl"))
    m = xgb.XGBClassifier(n_estimators=600, max_depth=6, learning_rate=0.05,
                          subsample=0.8, colsample_bytree=0.8, min_child_weight=5,
                          tree_method="hist", random_state=42, n_jobs=8)
    tr = tab[tab["split"] == "train"]
    m.fit(tr[STAT_FEATS].to_numpy(), tr["y"].to_numpy())
    Xte = tab[tab["split"] == "test"][STAT_FEATS].to_numpy()
    t0 = time.perf_counter()
    for _ in range(5): m.predict_proba(Xte[:4096])
    lat = (time.perf_counter() - t0) / 5 / 4096 * 1000
    e1 = json.load(open(os.path.join(RESULTS, f"e1_xgboost_T{T}.json")))
    out["xgboost"] = {"params": None, "n_trees": 600, "max_depth": 6,
                      "latency_ms_cpu_bs1": round(lat, 4),
                      "auprc": e1["auprc"], "auroc": e1["auroc"]}
    out["_note"] = ("latency measured on this laptop (RTX 3070 Ti / CPU); "
                    "indicative only, not an edge-MCU benchmark")
    save_json(out, "e2_compute.json")

    # Pareto figure: params vs AUPRC, marker size ~ latency
    fig, ax = plt.subplots(figsize=(7, 4.4))
    for k, v in out.items():
        if k.startswith("_") or v["params"] is None:
            continue
        ax.scatter(v["params"], v["auprc"], s=max(20, v["latency_ms_cpu_bs1"] * 40),
                   label=f"{k} ({v['latency_ms_cpu_bs1']:.1f} ms)")
        ax.annotate(k, (v["params"], v["auprc"]), textcoords="offset points",
                    xytext=(6, 4), fontsize=9)
    ax.axhline(out["xgboost"]["auprc"], color="gray", ls="--", lw=1)
    ax.text(20000, out["xgboost"]["auprc"] + 0.002, "XGBoost baseline", fontsize=8, color="gray")
    ax.set_xlabel("parameters (log)"); ax.set_xscale("log")
    ax.set_ylabel("test AUPRC (T=60)")
    ax.set_title("E2: accuracy vs model size (marker area ~ CPU latency)")
    ax.legend(fontsize=8, loc="lower right")
    fig.tight_layout(); fig.savefig(os.path.join(RESULTS, "fig_e2_pareto.png"), dpi=130)
    print(json.dumps({k: v for k, v in out.items() if not k.startswith("_")}, indent=2))

if __name__ == "__main__":
    main()
