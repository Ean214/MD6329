# -*- coding: utf-8 -*-
"""D1-NN: 1D-CNN+MLP (user's undergrad arch) / MLP / LSTM / Transformer-from-scratch.
Usage:
  python d1_nn.py --model cnnmlp --T 60          # full training
  python d1_nn.py --model transformer --T 60 --smoke --epochs 1   # verify pipeline
Models consume seq_T{T}.npz (X_seq, mask, X_stat, y, split).
"""
import argparse, json, math, os, sys, time
import numpy as np, torch, torch.nn as nn

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import BASE, DATA, RESULTS, SEED, metrics, save_json

DEV = "cuda" if torch.cuda.is_available() else "cpu"

# ---------------- data ----------------
def load_ds(T):
    d = np.load(os.path.join(DATA, f"seq_T{T}.npz"))
    return d

def standardize(d):
    Xs, m, Xst, y = d["X_seq"], d["mask"], d["X_stat"], d["y"]
    sp = d["split"]
    tr = sp == "train"
    # sequence feats: per-feature mean/std over valid train entries
    Xf = Xs.copy(); M = m[..., None]
    num = (Xf * M).sum(axis=(0, 1)); den = M.sum(axis=(0, 1)).clip(min=1)
    mu = num / den; sd = np.sqrt((((Xf - mu) * M) ** 2).sum(axis=(0, 1)) / den).clip(min=1e-6)
    Xf = (Xf - mu) / sd * M  # zero at pads
    # static feats
    mu_s = Xst[tr].mean(0); sd_s = Xst[tr].std(0).clip(min=1e-6)
    Xst = (Xst - mu_s) / sd_s
    return (Xf.astype(np.float32), m.astype(np.float32), Xst.astype(np.float32),
            y.astype(np.float32), sp, (mu, sd, mu_s, sd_s))

class DS(torch.utils.data.Dataset):
    def __init__(self, Xf, M, Xst, y):
        self.Xf, self.M, self.Xst, self.y = Xf, M, Xst, y
    def __len__(self): return len(self.y)
    def __getitem__(self, i):
        return (torch.from_numpy(self.Xf[i]), torch.from_numpy(self.M[i]),
                torch.from_numpy(self.Xst[i]), torch.tensor(self.y[i]))

# ---------------- models ----------------
class MLP(nn.Module):
    def __init__(self, fin, sdim):
        super().__init__()
        self.net = nn.Sequential(nn.Linear(sdim, 128), nn.ReLU(),
                                 nn.Dropout(0.2), nn.Linear(128, 64), nn.ReLU(),
                                 nn.Linear(64, 1))
    def forward(self, x, mask, s):
        return self.net(s).squeeze(-1)

class CNNMLP(nn.Module):
    """User's undergrad architecture: 1D-CNN branch (waveform) + MLP branch (static)
    fused by concatenation."""
    def __init__(self, fin, sdim):
        super().__init__()
        self.conv = nn.Sequential(
            nn.Conv1d(fin, 32, 5, padding=2), nn.ReLU(), nn.MaxPool1d(2),
            nn.Conv1d(32, 64, 5, padding=2), nn.ReLU())
        self.seq_head = nn.Linear(64, 64)
        self.stat = nn.Sequential(nn.Linear(sdim, 64), nn.ReLU())
        self.head = nn.Sequential(nn.Linear(128, 64), nn.ReLU(), nn.Dropout(0.2),
                                  nn.Linear(64, 1))
    def forward(self, x, mask, s):
        x = x.permute(0, 2, 1)                    # [B, F, L]
        h = self.conv(x * mask.unsqueeze(1))      # mask padded positions
        h = h.max(dim=2).values                   # global max pool
        h = self.seq_head(h)
        z = self.stat(s)
        return self.head(torch.cat([h, z], dim=1)).squeeze(-1)

class LSTMModel(nn.Module):
    def __init__(self, fin, sdim):
        super().__init__()
        self.proj = nn.Linear(fin, 32)
        self.lstm = nn.LSTM(32, 64, batch_first=True)
        self.stat = nn.Sequential(nn.Linear(sdim, 32), nn.ReLU())
        self.head = nn.Sequential(nn.Linear(96, 64), nn.ReLU(), nn.Dropout(0.2),
                                  nn.Linear(64, 1))
    def forward(self, x, mask, s):
        h, _ = self.lstm(self.proj(x))
        L = mask.sum(dim=1).long().clamp(min=1) - 1
        h = h[torch.arange(len(h)), L]
        return self.head(torch.cat([h, self.stat(s)], dim=1)).squeeze(-1)

class PositionalEncoding(nn.Module):
    def __init__(self, d, max_len=128):
        super().__init__()
        pe = torch.zeros(max_len, d)
        pos = torch.arange(max_len).unsqueeze(1).float()
        div = torch.exp(torch.arange(0, d, 2).float() * (-math.log(10000.0) / d))
        pe[:, 0::2] = torch.sin(pos * div); pe[:, 1::2] = torch.cos(pos * div)
        self.register_buffer("pe", pe.unsqueeze(0))
    def forward(self, x): return x + self.pe[:, :x.size(1)]

class TransformerIDH(nn.Module):
    """From-scratch Transformer encoder (adapted from MD6329 Assignment 2)."""
    def __init__(self, fin, sdim, d=64, heads=4, layers=2):
        super().__init__()
        self.proj = nn.Linear(fin, d)
        self.pe = PositionalEncoding(d)
        enc = nn.TransformerEncoderLayer(d, heads, d * 4, dropout=0.1,
                                         batch_first=True, norm_first=False)
        self.enc = nn.TransformerEncoder(enc, layers)
        self.stat = nn.Sequential(nn.Linear(sdim, 32), nn.ReLU())
        self.head = nn.Sequential(nn.Linear(d + 32, 64), nn.ReLU(), nn.Dropout(0.2),
                                  nn.Linear(64, 1))
    def forward(self, x, mask, s):
        h = self.pe(self.proj(x))
        key_padding = mask < 0.5                    # True = pad (PyTorch convention)
        h = self.enc(h, src_key_padding_mask=key_padding)
        m = mask.unsqueeze(-1)
        h = (h * m).sum(1) / m.sum(1).clamp(min=1)  # mean pool over valid
        return self.head(torch.cat([h, self.stat(s)], dim=1)).squeeze(-1)

MODELS = {"mlp": MLP, "cnnmlp": CNNMLP, "lstm": LSTMModel, "transformer": TransformerIDH}

# ---------------- train/eval ----------------
@torch.no_grad()
def infer(model, loader):
    model.eval(); ps, ys = [], []
    for x, mask, s, y in loader:
        x, mask, s = x.to(DEV), mask.to(DEV), s.to(DEV)
        ps.append(torch.sigmoid(model(x, mask, s)).cpu().numpy())
        ys.append(y.numpy())
    return np.concatenate(ps), np.concatenate(ys)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True, choices=list(MODELS))
    ap.add_argument("--T", type=int, default=60)
    ap.add_argument("--epochs", type=int, default=10)
    ap.add_argument("--bs", type=int, default=256)
    ap.add_argument("--lr", type=float, default=1e-3)
    ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args()
    torch.manual_seed(SEED); np.random.seed(SEED)

    d = load_ds(a.T)
    Xf, M, Xst, y, sp, _ = standardize(d)
    if a.smoke:
        idx = np.concatenate([
            np.flatnonzero(sp == "train")[:2000],
            np.flatnonzero(sp == "val")[:1000],
            np.flatnonzero(sp == "test")[:1000]])
        Xf, M, Xst, y, sp = Xf[idx], M[idx], Xst[idx], y[idx], sp[idx]
    tr = sp == "train"; va = sp == "val"; te = sp == "test"

    def loader(sel, shuffle=False):
        ds = DS(Xf[sel], M[sel], Xst[sel], y[sel])
        return torch.utils.data.DataLoader(ds, batch_size=a.bs, shuffle=shuffle,
                                           drop_last=shuffle)
    ltr, lva, lte = loader(tr, True), loader(va), loader(te)

    model = MODELS[a.model](Xf.shape[2], Xst.shape[1]).to(DEV)
    pos = torch.tensor([(y[tr] == 0).sum() / max(1, (y[tr] == 1).sum())], device=DEV)
    opt = torch.optim.Adam(model.parameters(), lr=a.lr)
    lossf = nn.BCEWithLogitsLoss(pos_weight=pos)
    best, best_state, bad = -1, None, 0
    t0 = time.time()
    for ep in range(a.epochs):
        model.train(); tot = 0.0
        for x, mask, s, yy in ltr:
            x, mask, s, yy = x.to(DEV), mask.to(DEV), s.to(DEV), yy.to(DEV)
            opt.zero_grad()
            loss = lossf(model(x, mask, s), yy)
            loss.backward(); opt.step(); tot += loss.item()
        pv, yv = infer(model, lva)
        mv = metrics(yv, pv)
        print(f"  ep{ep} loss={tot/len(ltr):.4f} val_auprc={mv['auprc']:.4f}", flush=True)
        if mv["auprc"] > best:
            best, bad = mv["auprc"], 0
            best_state = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}
        else:
            bad += 1
            if bad >= 2:
                break
    if best_state is not None:
        model.load_state_dict(best_state)
    pt, yt = infer(model, lte)
    res = metrics(yt, pt)
    res.update({"model": a.model, "horizon_T": a.T, "best_val_auprc": best,
                "train_time_s": round(time.time() - t0, 1),
                "n_params": sum(p.numel() for p in model.parameters()),
                "n_train": int(tr.sum()), "n_test": int(te.sum())})
    save_json(res, f"e1_{a.model}_T{a.T}.json")
    torch.save(best_state, os.path.join(RESULTS, f"ckpt_{a.model}_T{a.T}.pt"))
    print(json.dumps(res, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
