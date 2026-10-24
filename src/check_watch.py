# -*- coding: utf-8 -*-
"""Check which lecture-watch screenshots are still missing.

Expected files in docs/lecture_watch/: L1..L12, GL1, GL2 (.png/.jpg/.jpeg)
Usage: python src/check_watch.py [--open]
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIR = os.path.join(ROOT, "docs", "lecture_watch")
CITED = ["L1","L2","L3","L5","L6","L7","L8","L9","L10","L11","L12"]  # lectures cited in the report
OPTIONAL = ["L4", "GL1", "GL2"]                                        # not cited; evidence only
EXPECTED = CITED + (OPTIONAL if "--all" in sys.argv else [])
EXTS = (".png", ".jpg", ".jpeg")


def main():
    if not os.path.isdir(DIR):
        os.makedirs(DIR, exist_ok=True)
    found, missing = {}, []
    for name in EXPECTED:
        hit = next((f for f in os.listdir(DIR)
                    if os.path.splitext(f)[0].lower() == name.lower()
                    and f.lower().endswith(EXTS)), None)
        if hit:
            size = os.path.getsize(os.path.join(DIR, hit)) / 1024
            found[name] = (hit, size)
        else:
            missing.append(name)

    print(f"目录: {DIR}\n")
    print(f"{'讲次':<6}{'状态':<8}{'文件'}")
    print("-" * 46)
    for name in EXPECTED:
        if name in found:
            f, kb = found[name]
            print(f"{name:<6}{'OK':<8}{f}  ({kb:.0f} KB)")
        else:
            print(f"{name:<6}{'missing':<8}-")
    print("-" * 46)
    n_req = sum(1 for k in CITED if k in found)
    print(f"引用讲次完成 {n_req}/{len(CITED)}" + (f" | 含可选 {len(found)}/{len(EXPECTED)}" if "--all" in sys.argv else ""))

    if missing:
        print("\n还差: " + ", ".join(missing))
    else:
        print("\n全部齐了。")

    if "--open" in sys.argv:
        os.startfile(DIR)


if __name__ == "__main__":
    main()
