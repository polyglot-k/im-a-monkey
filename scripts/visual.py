"""im-a-monkey 시각 요소 검사. 사용: python3 scripts/visual.py FILE [--json]"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from textutil import Finding, _OFF_ON, fence_spans, line_col, strip_ignored  # noqa: E402

_MARKER = re.compile(r"<!--\s*visual:(.*?)-->", re.S)
_FIG_INFO = re.compile(r"(?:mermaid|svg)\b")
# 자기 닫는 svg → 닫는 태그까지 전체 → 닫히지 않았으면 여는 태그만 순서로 맞춘다.
_FIG_INLINE = re.compile(r"<svg\b[^>]*/>|<svg\b.*?</svg>|<svg\b[^>]*>|!\[[^\]]*\]\([^)]*\)", re.S)
_CAPTION = re.compile(r"^(?:<(?:p|figcaption)\b[^>]*>\s*)?\*?\s*그림 \d+\.\s*(.*)$")
_CLOSE_TAGS = re.compile(r"(?:\s*</(?:p|figcaption|figure)>)+\s*$")
_FIRST_SENT = re.compile(r"^.*?[.?!]\*?(?=\s|$)")
_HEAD = re.compile(r"^#{1,6}[ \t]+\S.*$", re.M)
_CALLOUT = re.compile(r"^[ \t]*> \[!", re.M)
_BADGE = re.compile(r"\[(?:측정|추정|미확인)\]")


def _caption_ok(orig: str, end: int) -> bool:
    # 그림이 끝난 줄의 나머지부터 본다: <figure> 안에서 </svg> 뒤에 바로 <figcaption>이 오는 경우.
    for ln in orig[end:].split("\n"):
        if not ln.strip():
            continue
        m = _CAPTION.match(ln.strip())
        if not m:
            return False
        rest = _CLOSE_TAGS.sub("", m.group(1)).rstrip("*").strip()
        s = _FIRST_SENT.match(rest)
        return (s.group(0) if s else rest).rstrip("*").endswith("?")
    return False


def check(text: str) -> list[Finding]:
    orig = text.replace("\r\n", "\n")
    s = strip_ignored(text)
    off = [m.span() for m in _OFF_ON.finditer(orig)]
    found = []

    def add(fid: str, pos: int, msg: str) -> None:
        line, col = line_col(orig, pos)
        ex = orig[pos:pos + 40].split("\n")[0]
        found.append(Finding(fid, line, col, ex, msg))

    for m in _MARKER.finditer(s):
        add("V01", m.start(), "초안 마커가 남아 있다")
        kind = m.group(1).split("|")[0].strip()
        if kind == "compare" and "강조:" not in m.group(1):
            add("V03", m.start(), "compare 마커에 강조가 없다")

    figs = [(a, b) for a, b, info in fence_spans(orig)
            if _FIG_INFO.match(info) and not any(x <= a < y for x, y in off)]
    figs += [(m.start(), m.end()) for m in _FIG_INLINE.finditer(s)]
    for start, end in figs:
        if not _caption_ok(orig, end):
            add("V02", start, "그림 바로 아래에 '그림 N. <질문?>' 캡션이 없다")

    heads = [m.start() for m in _HEAD.finditer(s)]
    bounds = [0] + heads + [len(s)]
    for i in range(len(bounds) - 1):
        a, b = bounds[i], bounds[i + 1]
        sec = s[a:b]
        n = len(_CALLOUT.findall(sec)) + len(_BADGE.findall(sec))
        if n > 2:
            add("V04", a, f"한 섹션에 콜아웃·배지가 {n}개다(2개 이하)")
    return sorted(found, key=lambda f: (f.line, f.col))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("file")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    with open(a.file, encoding="utf-8", newline="") as f:
        found = check(f.read())
    if a.json:
        print(json.dumps([f.__dict__ for f in found], ensure_ascii=False))
    else:
        for f in found:
            print(f)
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
