"""im-a-monkey 리듬 측정. 사용: python3 scripts/rhythm.py FILE [--json] (항상 종료 코드 0)"""
from __future__ import annotations

import argparse
import json
import os
import re
import statistics
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from textutil import eojeol_count, strip_ignored  # noqa: E402

_BULLET = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s")
_SPLIT = re.compile(r"(?<=[.?!])\s+")
_BOLD = re.compile(r"\*\*[^*\n]+\*\*")
_TAIL = re.compile(r"[.?!\s]+$")


def _lines(text: str) -> list[str]:
    return [ln for ln in strip_ignored(text).split("\n")
            if ln.strip() and not ln.lstrip().startswith(("#", "|"))]


def split_sentences(text: str) -> list[str]:
    out = []
    for ln in _lines(text):
        if _BULLET.match(ln):
            out.append(ln.strip())
        else:
            out.extend(s for s in _SPLIT.split(ln.strip()) if s)
    return out


def _ending(s: str) -> str:
    return _TAIL.sub("", s)[-2:]


def measure(text: str) -> dict:
    sents = split_sentences(text)
    lens = [eojeol_count(s) for s in sents]
    lines = _lines(text)
    run = best = 0
    prev = None
    for s in sents:
        e = _ending(s)
        run = run + 1 if e == prev else 1
        prev = e
        best = max(best, run)
    words = sum(lens)
    return {
        "sentences": len(sents),
        "mean_eojeol": statistics.mean(lens) if lens else 0.0,
        "stdev_eojeol": statistics.pstdev(lens) if lens else 0.0,
        "max_same_ending_run": best,
        "bullet_ratio": sum(1 for ln in lines if _BULLET.match(ln)) / len(lines) if lines else 0.0,
        "bold_per_100": len(_BOLD.findall(strip_ignored(text))) * 100 / words if words else 0.0,
        "long_sentences": [i + 1 for i, n in enumerate(lens) if n > 40],
    }


def flags(m: dict) -> list[str]:
    out = []
    if m["stdev_eojeol"] < 2.5 and m["sentences"] >= 6:
        out.append("A15 문장 길이가 고르다")
    if m["max_same_ending_run"] >= 4:
        out.append(f"A15 같은 어미 연속 {m['max_same_ending_run']}회")
    if m["bullet_ratio"] > 0.6:
        out.append(f"A16 불릿 비율 {m['bullet_ratio']:.0%}")
    if m["bold_per_100"] > 3:
        out.append("A16 볼드 과다")
    if m["long_sentences"]:
        out.append("긴 문장(경고): " + ", ".join(map(str, m["long_sentences"])))
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("file")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    with open(args.file, encoding="utf-8") as f:
        m = measure(f.read())
    fl = flags(m)
    if args.json:
        print(json.dumps({**m, "flags": fl}, ensure_ascii=False))
    else:
        for k, v in m.items():
            print(f"{k}: {round(v, 2) if isinstance(v, float) else v}")
        for x in fl:
            print(x)
    return 0


if __name__ == "__main__":
    sys.exit(main())
