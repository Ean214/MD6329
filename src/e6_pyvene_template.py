# -*- coding: utf-8 -*-
"""
MD6329 Deep Learning for Healthcare AI -- final course project.
Generative AI assistance was used in writing this script, as disclosed in the
report (Section 4, "Software 3.0") and on the project cover page. The author
validated the implementation and the results, and remains responsible for both.
"""
"""E6-arm2: pyvene layer-wise ZeroIntervention on the from-scratch Transformer.
Run AFTER d1_nn.py --model transformer has produced ckpt_transformer_T60.pt.

PyVene 0.1.8 pitfalls (from MD6329 A2, see skill pytorch-arch-ab-experiment):
  - intervention = pv.ZeroIntervention()  # INSTANCE, not class
  - unit_locations sources->base target must be 3-D (1, 1, P)
  - pyvene leaves hooks attached: snapshot hook ids before, remove only the
    new ones afterwards (by set difference)
  - measure on LOGIT scale; sigmoid saturates (p~0.9999 -> slope 5.7e-05)
"""
import json, os, sys
import numpy as np, torch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import DATA, RESULTS, SEED, save_json
import pyvene as pv
from d1_nn import TransformerIDH, load_ds, standardize, infer

T = int(sys.argv[1]) if len(sys.argv) > 1 else 60

def main():
    d = load_ds(T)
    Xf, M, Xst, y, sp, _ = standardize(d)
    te = sp == "test"
    Xf_t = torch.from_numpy(Xf[te]).cuda()
    M_t = torch.from_numpy(M[te]).cuda()
    S_t = torch.from_numpy(Xst[te]).cuda()

    model = TransformerIDH(Xf.shape[2], Xst.shape[1]).cuda()
    ckpt = torch.load(os.path.join(RESULTS, f"ckpt_transformer_T{T}.pt"),
                      map_location="cuda")
    model.load_state_dict(ckpt)
    model.eval()

    with torch.no_grad():
        base_logit = model(Xf_t, M_t, S_t).cpu().numpy()
    base_prob = 1 / (1 + np.exp(-base_logit))

    n_layers = 2
    results = []
    for layer in range(n_layers):
        for comp_name, comp_path in [("attn", f"layers.{layer}.self_attn.out_proj"),
                                      ("ffn", f"layers.{layer}.linear2")]:
            cfg = pv.IntervenableConfig(
                representations=[pv.RepresentationConfig(
                    layer=0, component=comp_path.replace("layers.0.", ""),
                    intervention=pv.ZeroIntervention(),
                    unit="pos", max_number_of_units=16)],
                model_type=None)
            # NOTE: pyvene wraps models via IntervenableModel; for a custom
            # nn.Module it must be registered. If registration fails, use the
            # manual-ablation fallback below instead.
            results.append({"layer": layer, "component": comp_name,
                            "status": "template-see-fallback"})
    # --- manual ablation fallback (works without pyvene registration) ---
    manual = []
    with torch.no_grad():
        for layer in range(n_layers):
            for comp in ["attn", "ffn"]:
                handles = []
                def mk_hook():
                    def hook(module, inp, out):
                        if isinstance(out, tuple):  # MHA returns (attn_out, weights)
                            return (torch.zeros_like(out[0]),) + out[1:]
                        return torch.zeros_like(out)
                    return hook
                mod = model.enc.layers[layer]
                target = mod.self_attn.out_proj if comp == "attn" else mod.linear2
                handles.append(target.register_forward_hook(mk_hook()))
                logits = model(Xf_t, M_t, S_t).cpu().numpy()
                for h in handles:
                    h.remove()
                dp = base_prob - (1 / (1 + np.exp(-logits)))
                manual.append({"layer": layer, "component": comp,
                               "mean_logit_drop": float((base_logit - logits).mean()),
                               "mean_prob_drop": float(dp.mean()),
                               "frac_flipped": float(((dp > 0.1)).mean())})
    save_json({"pyvene_template": results, "manual_ablation": manual},
              f"e6_pyvene_T{T}.json")
    print(json.dumps(manual, indent=2))

if __name__ == "__main__":
    main()
