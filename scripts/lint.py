"""im-a-monkey 린터. 사용: python3 scripts/lint.py FILE... [--type TYPE] [--json]"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from patterns import PATTERNS  # noqa: E402
from textutil import Finding, eojeol_count, line_col, run_files, strip_ignored  # noqa: E402

TYPE_LIMITS = {
    "decision": 1500, "adr": 400, "report": 800, "explain": 1000,
    "howto": 600, "reference": 500, "message": 150, "study": None,
}
TYPE_MINIMUMS = {
    "decision": 300, "adr": 150, "report": 200, "explain": 200,
    "howto": 100, "reference": 80, "message": None, "study": 400,
}

_MAP_HEAD = re.compile(r"^(#{1,6})[ \t]+코드 읽기 지도[ \t]*$", re.M)
_HEAD = re.compile(r"^(#{1,6})[ \t]+\S", re.M)


def _map_ranges(s: str) -> list[tuple[int, int]]:
    out = []
    for m in _MAP_HEAD.finditer(s):
        level = len(m.group(1))
        end = len(s)
        for h in _HEAD.finditer(s, m.end()):
            if len(h.group(1)) <= level:
                end = h.start()
                break
        out.append((m.start(), end))
    return out


def lint_text(text: str, doc_type: str | None = None) -> list[Finding]:
    orig = text.replace("\r\n", "\n")
    s = strip_ignored(text)
    skip = _map_ranges(s)
    found = []
    for pid, rx, msg in PATTERNS:
        for m in rx.finditer(s):
            if pid == "T03" and any(a <= m.start() < b for a, b in skip):
                continue
            line, col = line_col(orig, m.start())
            ex = orig[max(0, m.start() - 10):m.end() + 10].replace("\n", " ")
            found.append(Finding(pid, line, col, ex, msg))
    if doc_type:
        n = eojeol_count(s)
        limit, low = TYPE_LIMITS.get(doc_type), TYPE_MINIMUMS.get(doc_type)
        if limit is not None and n > limit:
            found.append(Finding("L01", 1, 1, "", f"{n}어절 / 상한 {limit}: 줄이지 말고 나누세요"))
        if low is not None and n < low:
            found.append(Finding("L02", 1, 1, "", f"{n}어절 / 하한 {low}: 빠진 맥락이 없는지 보세요"))
    return sorted(found, key=lambda f: (f.line, f.col))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="+", metavar="FILE", help="파일 또는 폴더(*.md 재귀)")
    ap.add_argument("--type", choices=sorted(TYPE_LIMITS))
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    return run_files(a.files, lambda t: lint_text(t, a.type), a.json)


if __name__ == "__main__":
    sys.exit(main())
