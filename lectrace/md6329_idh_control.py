# -*- coding: utf-8 -*-
"""
MD6329 Deep Learning for Healthcare AI -- final course project.
Generative AI assistance was used in writing this script, as disclosed in the
report (Section 4, "Software 3.0") and on the project cover page. The author
validated the implementation and the results, and remains responsible for both.
"""
"""MD6329 Final Project — LecTrace execution-explanation presentation.

Sensor-light closed-loop ultrafiltration control in haemodialysis.
Five execution states, each a place where a silent mistake would invalidate a
headline number. Run:

    python lectrace/md6329_idh_control.py      # plain script
    lectrace serve                             # interactive viewer
"""
import json
import os
import sys

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from lectrace import text, note, plot, table

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
RES = os.path.join(ROOT, "results")
T_DECISION = 60.0
GAP_HOURS = 6.0


def main():
    text("# Sensor-light closed-loop ultrafiltration control in haemodialysis")
    text("An in-silico feasibility study on routine dialysis-machine data "
         "(HEMOBP, CC BY 4.0).")
    text("**Problem.** Ultrafiltration removes fluid faster than the capillaries "
         "refill them, and intradialytic hypotension (IDH) follows. Existing "
         "closed-loop devices already adjust the ultrafiltration rate, but they "
         "depend on an optical relative-blood-volume sensor a wearable cannot carry.")
    text("**Question.** With routinely recorded machine data only, can a "
         "predict-then-adjust loop be built — and what does it cost?")
    note("Every control number in this presentation is **in silico**, under a "
         "model trained on clinicians' own decisions. Not clinical validation.")

    text("## Why these five states")
    text("Each state below is a place where a silent mistake would invalidate a "
         "headline number. The loss curve looks healthy even when the evaluation "
         "is wrong, so I show the checks instead.")

    # ---------------- State 1 ----------------
    text("## State 1 — Reconstructing a session (the midnight trap)")
    text("Sessions are *not* calendar days: the unit runs three shifts and the "
         "last one crosses midnight.")
    readings, raw_day_count, session_count = cut_into_sessions()
    table([
        ["on-disk file", os.path.basename(os.path.join(DATA, "lectrace_readings.csv"))],
        ["patient pid", "102117"],
        ["rows read", len(readings)],
        ["rows = distinct calendar days (WRONG)", raw_day_count],
        ["rows = contiguous runs (CORRECT)", session_count],
    ], headers=["quantity", "value"])
    note("Keying on the calendar date splits midnight-crossing sessions in two. "
         "On the full cohort that inflates the session count by ~44% and silently "
         "turns the weight fields into NaN on half the data.")

    # ---------------- State 2 ----------------
    text("## State 2 — The leakage boundary at T = 60 min")
    text("Readings up to `T` are the *input*. Readings after `T` build the "
         "*label*. If this boundary slips by one row, every score becomes "
         "meaningless.")
    pre, post, pre_nadir, post_nadir = apply_boundary(readings, T_DECISION)
    table([
        ["input rows (time <= T)", len(pre)],
        ["label rows (time > T)", len(post)],
        ["nadir SBP before T (input only)", round(pre_nadir, 1)],
        ["nadir SBP after T (label only)", round(post_nadir, 1)],
        ["label: IDH after T?", bool(post_nadir < 90)],
    ], headers=["quantity", "value"])
    note("If the pre-decision nadir is already below 90 mmHg the prediction is "
         "moot, so such sessions are dropped — the cohort keeps 147,044 samples "
         "at T = 60 min.")

    # ---------------- State 3 ----------------
    text("## State 3 — Splitting by patient, not by row")
    text("One patient contributes dozens of sessions. Row-wise splitting leaks.")
    overlaps = check_group_split()
    table([["patients in train/test overlap", overlaps[0]],
           ["patients in val/test overlap", overlaps[1]],
           ["test prevalence (IDH at T=60)", overlaps[2]]],
          headers=["check", "value"])
    note("Rows, unlike patients, are not independent. Test prevalence (5.86%) is "
         "lower than validation prevalence, which is why AUPRC must never be "
         "compared across sets with different prevalence.")

    # ---------------- State 4 ----------------
    text("## State 4 — One decision point in the control simulation")
    text("At `T` the controller compares candidate ultrafiltration rates and "
         "picks the one minimising predicted risk subject to a residual-fluid "
         "tolerance. Here is one session's fluid accounting.")
    accounting = one_decision_point()
    table(accounting["rows"], headers=["quantity", "value"])
    text("The three policies, evaluated over the whole test set (tolerance 0.5 L):")
    table(accounting["policies"],
          headers=["policy", "predicted IDH risk", "residual fluid", "extra time"])
    plot(tradeoff_figure())
    note("Switching from constant to predictive ultrafiltration lowers predicted "
         "risk by 19.5% relative — and costs 258 mL of unremoved fluid plus about "
         "104 extra minutes. **That price is the finding.**")

    # ---------------- State 5 ----------------
    text("## State 5 — The ablation that surprised me")
    text("Zeroing a component is an *intervention*; reading attention weights is "
         "only an *observation*. They disagree here.")
    rows, slope_note = intervention_and_saturation()
    table(rows, headers=["zeroed component", "mean logit change", "verdict"])
    note(slope_note)
    text("The predictive signal flows through the feed-forward path, not through "
         "attention. So attention-heavy architectures are hard to justify here — "
         "and attention maps must not be presented as clinical explanations.")

    # ---------------- Close ----------------
    text("## What this buys, and what it does not")
    text("**Buys:** IDH is predictable from routine data at a 60-minute horizon "
         "(AUPRC 0.2015 versus 0.0586 prevalence); the design project's compact "
         "1D-CNN+MLP captures 91% of the best model at a quarter of the "
         "parameters; only intra-session blood pressure is indispensable.")
    text("**Does not buy:** causality. The ultrafiltration dose-response is "
         "monotone and clinically plausible, yet equally consistent with "
         "confounding by indication. The retrospective data cannot separate them.")
    note("That boundary is why a clinician-set safety envelope with a physical "
         "override is a necessary condition of the design, not a bureaucratic "
         "decoration — and why the next step is a prospective study.")


# --------------------------------------------------------------------------
# helper functions (shown in the viewer only when main() calls them)
# --------------------------------------------------------------------------

def cut_into_sessions():
    """State 1: cut one patient's readings into sessions at a 6-hour gap."""
    path = os.path.join(DATA, "lectrace_readings.csv")
    if not os.path.exists(path):
        raise FileNotFoundError("run: python src/make_lectrace_data.py first")
    df = pd.read_csv(path, parse_dates=["datatime"])
    df = df[df["pid"] == 102117].sort_values("datatime").reset_index(drop=True)
    calendar_days = df["datatime"].dt.date.nunique()
    gap_hours = df["datatime"].diff().dt.total_seconds() / 3600.0
    new_session = (gap_hours > GAP_HOURS) | gap_hours.isna()
    sessions = int(new_session.sum())
    df["session"] = new_session.cumsum()
    print(f"  calendar days (wrong) = {calendar_days}; contiguous runs (right) = {sessions}")
    return df, calendar_days, sessions


def apply_boundary(readings, T):
    """State 2: split input from label at the decision point."""
    pre = readings[readings["time"] <= T]
    post = readings[readings["time"] > T]
    print(f"  input rows = {len(pre)}, label rows = {len(post)}")
    return pre, post, float(pre["sbp"].min()), float(post["sbp"].min())


def check_group_split():
    """State 3: verify no patient appears in two splits."""
    sys.path.insert(0, os.path.join(ROOT, "src"))
    from common import patient_split
    split = patient_split(os.path.join(RES, "sessions.csv"))
    tr = {p for p, s in split.items() if s == "train"}
    va = {p for p, s in split.items() if s == "val"}
    te = {p for p, s in split.items() if s == "test"}
    tab = pd.read_pickle(os.path.join(DATA, "tabular_T60.pkl"))
    test_prev = round(float(tab[tab["split"] == "test"]["y"].mean()), 4)
    print(f"  overlap train/test = {len(tr & te)}, val/test = {len(va & te)}")
    return len(tr & te), len(va & te), test_prev


def one_decision_point():
    """State 4: fluid accounting for one test session + the policy outcomes."""
    tab = pd.read_pickle(os.path.join(DATA, "tabular_T60.pkl"))
    te = tab[(tab["split"] == "test") & (tab["mean_uf_post"] > 0.2)].copy()
    removed_pre = te["mean_uf_so_far"] * (T_DECISION / 60.0)
    te["target_left"] = (te["idwg"] - removed_pre).clip(lower=0)
    te["hours_left"] = te["remaining_min"] / 60.0
    te["residual"] = (te["target_left"] - te["mean_uf_post"] * te["hours_left"]).clip(lower=0)
    # pick a session where the clinician's own plan still left fluid behind,
    # so the demonstration is informative rather than trivially complete
    row = te[te["residual"] > 0.2].iloc[0]
    removed_pre = row["mean_uf_so_far"] * (T_DECISION / 60.0)
    target_left = max(row["idwg"] - removed_pre, 0.0)
    hours_left = row["remaining_min"] / 60.0
    actual_left = target_left - row["mean_uf_post"] * hours_left
    rows = [
        ["interdialytic weight gain (fluid to remove)", f"{row['idwg']:.2f} L"],
        ["removed in the first hour (estimate)", f"{removed_pre:.2f} L"],
        ["still to remove at T", f"{target_left:.2f} L"],
        ["remaining session time", f"{hours_left:.2f} h"],
        ["actual post-T ultrafiltration rate", f"{row['mean_uf_post']:.2f} L/h"],
        ["residual fluid under the actual plan", f"{max(actual_left, 0) * 1000:.0f} mL"],
        ["outcome: IDH after T?", bool(row["y"])],
    ]
    sim = json.load(open(os.path.join(RES, "e5_tradeoff.json")))["T60"]["tol_0.5L"]
    labels = {"constant": "constant UFR (current practice)",
              "reactive": "reactive rule (biofeedback proxy)",
              "predictive": "predictive (model-chosen UFR)"}
    policies = [[labels[k], f"{sim[k]['risk']:.3f}",
                 f"{sim[k]['resid_mL']:.0f} mL", f"{sim[k]['ext_min']:.0f} min"]
                for k in ["constant", "reactive", "predictive"]]
    print("  residual fluid under the actual plan:", f"{max(actual_left,0)*1000:.0f} mL")
    return {"rows": rows, "policies": policies}


def tradeoff_figure():
    """State 4 figure: risk against residual fluid for three policies."""
    sim = json.load(open(os.path.join(RES, "e5_tradeoff.json")))["T60"]["tol_0.5L"]
    fig, ax = plt.subplots(figsize=(5.2, 3.4))
    for key, colour, lab in [("constant", "#888888", "constant"),
                             ("reactive", "#c9862f", "reactive"),
                             ("predictive", "#2a8f6b", "predictive")]:
        ax.scatter(sim[key]["resid_mL"], sim[key]["risk"], s=90, color=colour, zorder=3)
        ax.annotate(lab, (sim[key]["resid_mL"], sim[key]["risk"]),
                    textcoords="offset points", xytext=(7, 4), fontsize=8)
    ax.set_xlabel("residual fluid not removed (mL)")
    ax.set_ylabel("predicted IDH risk")
    ax.set_title("The trade-off no one had quantified", fontsize=10)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    return fig


def intervention_and_saturation():
    """State 5: attention vs feed-forward ablation, plus the saturation lesson."""
    abl = json.load(open(os.path.join(RES, "e6_pyvene_T60.json")))["manual_ablation"]
    rows = []
    for r in abl:
        change = r["mean_logit_drop"]
        verdict = "≈ none" if abs(change) < 1e-3 else "real effect"
        rows.append([f"layer {r['layer']} {r['component']}", f"{change:.3g}", verdict])
    p = 0.9999
    slope = p * (1 - p)
    note_text = (f"Lesson from an earlier assignment: at a predicted probability of "
                 f"{p}, the sigmoid slope p(1-p) is {slope:.2g}. Any real change is "
                 f"compressed to nothing on the probability scale — which is why all "
                 f"ablation reporting here is on the logit scale.")
    print("  sigmoid slope at p=0.9999:", f"{slope:.2g}")
    return rows, note_text


if __name__ == "__main__":
    main()
