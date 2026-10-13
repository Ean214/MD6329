# -*- coding: utf-8 -*-
"""
MD6329 Deep Learning for Healthcare AI -- final course project.
Generative AI assistance was used in writing this script, as disclosed in the
report (Section 4, "Software 3.0") and on the project cover page. The author
validated the implementation and the results, and remains responsible for both.
"""
"""Create a small readings extract so the LecTrace lecture runs in seconds
instead of loading the 262 MB vip.csv each time."""
import os, sys
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import BASE, DATA

OUT = os.path.join(DATA, "lectrace_readings.csv")
PIDS = [102117, 10156632]

def main():
    if os.path.exists(OUT):
        print("exists:", OUT); return
    vip = pd.read_csv(os.path.join(BASE, "hemobp", "vip.csv"),
                      usecols=["pid", "datatime", "time", "sbp", "dbp", "uf", "blood_flow"],
                      dtype={"sbp": "float32", "dbp": "float32", "uf": "float32",
                             "blood_flow": "float32", "time": "float32"})
    sub = vip[vip["pid"].isin(PIDS)].sort_values(["pid", "datatime"])
    sub.to_csv(OUT, index=False)
    print(f"wrote {OUT}: {len(sub):,} rows, {sub['pid'].nunique()} patients")

if __name__ == "__main__":
    main()
