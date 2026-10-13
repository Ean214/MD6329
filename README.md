# Sensor-Light Closed-Loop Ultrafiltration Control in Haemodialysis

Code, results and presentation for the MD6329 *Deep Learning for Healthcare AI* final course project
(NTU LKCMedicine, AY2026-27). Author: **LE YI** (G2605168D).

## What this is

An in-silico feasibility study of a predict-then-adjust ultrafiltration (UF) control loop for
haemodialysis, using **routinely recorded machine data only** — no optical relative-blood-volume
sensor. The motivating question comes from a wearable artificial-kidney design project: existing
clinical closed-loop systems (Hemocontrol, BVM biofeedback) work, but their sensor does not fit a
wearable, so what can be done without it — and what does that cost?

**Headline results (HEMOBP, 1,072 patients / 197,269 reconstructed sessions):**

| Question | Result |
|---|---|
| Can IDH be predicted from routine data? | Yes. Best 60-min model AUPRC **0.2015** vs 0.0586 prevalence, AUROC 0.774 |
| Is a heavy model needed? | No. The design project's 1D-CNN+MLP reaches **91%** of the Transformer's AUPRC with **1/4** the parameters and **44x** less batch latency |
| Is multi-modal sensing necessary? | Only intra-session blood pressure is indispensable; removing it costs **44%** of AUPRC |
| What does prediction buy, and cost? | Predicted IDH risk **0.238 -> 0.192** (-19.5%), but **+258 mL** unremoved fluid and **~104 extra minutes** |
| Can the control policy be validated? | **No.** The UF dose-response is equally consistent with confounding by indication |

Everything control-related is **in silico**, under a dynamics model trained on clinicians' own
decisions. It is not clinical validation.

## Layout

```
data/          modelling datasets (seq_T*.npz, tabular_T*.pkl); see data/README.md for raw data
src/           pipeline scripts, numbered by stage (p0 -> d0 -> d1 -> e2..e6)
results/       JSON results and figures — the single source for every number in the report
report/        NeurIPS-format report (main.tex, main.pdf) and the official cover page
lectrace/      LecTrace execution-explanation presentation (5 states)
docs/          pipeline plan, dataset card, claims register, lecture index, references, interview sheet
```

## Reproducing

```bash
python src/p0_eda.py                 # session reconstruction + EDA
python src/d0_build_dataset.py       # build samples for T = 30/60/90/120
python src/d1_xgboost.py 60          # tabular baseline
python src/d1_nn.py --model cnnmlp --T 60 --epochs 10
python src/e2_compute.py             # params / FLOPs / latency
python src/e3_e4.py both             # horizon curve + modality ablation
python src/e5_control.py 60 90 120   # control trade-off (core result)
python src/e6_causal.py 60           # confounding probes
python src/e6_pyvene_template.py 60  # intervention-style ablation
python lectrace/md6329_idh_control.py
lectrace build                       # static viewer in _site/
```

## Data

HEMOBP (Lin et al., *Scientific Data* 6:313, 2019), **CC BY 4.0**, figshare article 6260654.
Raw files are not committed; see `data/README.md`. Please cite the original paper if you reuse them.

## AI assistance

Generative AI assistance was used and is disclosed in the report's *Software 3.0* section and on the
cover page, per the course honour code.
