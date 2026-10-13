# -*- coding: utf-8 -*-
"""R2: fetch EN auto-captions for the 14 lectures via yt-dlp (more reliable
than youtube-transcript-api which returns ParseError under bot-check).
Outputs: results/transcripts/<videoId>.en.vtt + .txt (timestamped lines)
Usage: python fetch_transcripts.py [videoId ...]   (default: all 14)
"""
import os, re, subprocess, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import RESULTS

PLAYLIST = [
    ("IZaCn61abYk", "L1_DL4HC_intro"),
    ("Ki2h4rNHuSk", "L2_medimg_classification"),
    ("Qumo5ZubHcE", "L3_classification_segmentation"),
    ("CnVvOjqqJpw", "L4_advanced_vision"),
    ("Ixk0KP0TZfw", "L5_EHR_intro"),
    ("AeDzGhM1GBU", "L6_RNN_LSTM"),
    ("B2R-MXhdRgM", "L7_transformer_BERT"),
    ("E5X3YW451Rs", "L8_multimodal_contrastive"),
    ("gBp-2rKQ1hY", "L9_GPT_CLIP"),
    ("72nHQ-2g718", "L10_unsup_RL"),
    ("DDU159QXVzI", "L11_interpretability_ethics"),
    ("D-7JVn0jwhQ", "L12_federated_privacy"),
    ("pJhVXVkP59E", "GL1_xiao_mingqing_msra"),
    ("CsVlfd8n0gg", "GL2_git_kim_ann"),
]
YT = r"C:\Users\LEYI\.workbuddy\binaries\python\envs\default\Scripts\yt-dlp.exe"
OUTDIR = os.path.join(RESULTS, "transcripts")

def vtt_to_txt(vtt_path, txt_path):
    lines, last = [], None
    with open(vtt_path, encoding="utf-8", errors="ignore") as f:
        for ln in f:
            m = re.match(r"(\d{2}):(\d{2}):(\d{2})\.\d+\s+-->", ln)
            if not m:
                continue
            t = int(m.group(1)) * 3600 + int(m.group(2)) * 60 + int(m.group(3))
            text = next(f, "").strip()
            text = re.sub(r"<[^>]+>", "", text)
            if text and text != last:
                lines.append(f"[{t//60:02d}:{t%60:02d}] {text}")
                last = text
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

def main():
    os.makedirs(OUTDIR, exist_ok=True)
    ids = sys.argv[1:]
    todo = [p for p in PLAYLIST if not ids or p[0] in ids]
    for vid, name in todo:
        out = os.path.join(OUTDIR, f"{name}.{vid}")
        r = subprocess.run([YT, "--write-auto-subs", "--sub-langs", "en",
                            "--sub-format", "vtt", "--skip-download",
                            "-o", out,
                            f"https://www.youtube.com/watch?v={vid}"],
                           capture_output=True, text=True, timeout=300)
        vtt = out + ".en.vtt"
        if os.path.exists(vtt):
            vtt_to_txt(vtt, out + ".txt")
            n = sum(1 for _ in open(out + ".txt", encoding="utf-8"))
            print(f"OK {name}: {n} lines", flush=True)
        else:
            print(f"FAIL {name}: {r.stderr[-200:]}", flush=True)

if __name__ == "__main__":
    main()
