"""im-a-monkey 리듬 측정. 사용: python3 scripts/rhythm.py FILE [--json] (항상 종료 코드 0)"""
from __future__ import annotations

import argparse
import html
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
_HTML_DROP = re.compile(r"<(style|script|svg|table|h[1-6])\b.*?</\1>|<!--.*?-->", re.S | re.I)
_HTML_BLOCK = re.compile(r"</?(p|div|li|h[1-6]|tr|td|th|br|section|header|footer|table|ul|ol|figcaption|blockquote)\b[^>]*>", re.I)
_HTML_TAG = re.compile(r"<[^>]+>")


def _html_text(text: str) -> str:
    # ponytail: 정규식으로 태그만 벗긴다. 본문 문장 리듬만 재면 돼서 파서는 두지 않는다.
    # 마크다운처럼 표·제목은 빼고, 문장 부호로 끝나지 않는 조각(그림 라벨 등)도 뺀다.
    text = html.unescape(_HTML_TAG.sub("", _HTML_BLOCK.sub("\n", _HTML_DROP.sub("", text))))
    return "\n".join(ln for ln in text.split("\n") if re.search(r"[.?!]\s*$", ln))


def _lines(text: str) -> list[str]:
    return [ln for ln in strip_ignored(text).split("\n")
            if ln.strip() and not ln.lstrip().startswith(("#", "|", "<"))]


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
    if re.search(r"<(html|body)\b", text, re.I):
        text = _html_text(text)
    sents = split_sentences(text)
    lens = [eojeol_count(s) for s in sents]
    lines = _lines(text)
    run = best = 0
    prev = None
    ends = [_ending(s) for s in sents]
    for e in ends:
        run = run + 1 if e == prev else 1
        prev = e
        best = max(best, run)
    top = max((ends.count(e) for e in set(ends)), default=0)
    words = sum(lens)
    return {
        "sentences": len(sents),
        "mean_eojeol": statistics.mean(lens) if lens else 0.0,
        "stdev_eojeol": statistics.pstdev(lens) if lens else 0.0,
        "max_same_ending_run": best,
        "variation_endings": {v: sum(1 for x in sents if re.search(v + r"[.?!]?\W*$", x)) for v in _VARIATION},
        "top_ending_share": top / len(sents) if sents else 0.0,
        "long_100char_share": sum(1 for s in sents if len(s) >= 100) / len(sents) if sents else 0.0,
        "bullet_ratio": sum(1 for ln in lines if _BULLET.match(ln)) / len(lines) if lines else 0.0,
        "bold_per_100": len(_BOLD.findall(strip_ignored(text))) * 100 / words if words else 0.0,
        "long_sentences": [i + 1 for i, n in enumerate(lens) if n > 40],
    }


# 어미를 섞으려다 한 가지 변주 어미로 몰리는 것도 반복이다.
_VARIATION = ("죠", "거든요", "잖아요", "네요")


def flags(m: dict) -> list[str]:
    out = []
    flat = m["stdev_eojeol"] < 2.5
    if flat and m["sentences"] >= 6:
        out.append("A15 문장 길이가 고르다")
    if m["max_same_ending_run"] >= 4:
        out.append(f"A15 같은 어미 연속 {m['max_same_ending_run']}회")
    # 합니다체·해요체도 예외 없이 센다. 같은 말투 안에서 어미를 바꿔 쓰는 게 고치는 방법이다.
    if m["sentences"] >= 10 and m["top_ending_share"] >= 0.4:
        out.append(f"A15 같은 어미 비율 {m['top_ending_share']:.0%}")
    if m["sentences"] >= 15 and m["long_100char_share"] < 0.05:
        out.append("A15 긴 문장이 거의 없음: 붙어 다니는 두 문장을 이어 쓰세요")
    for v, n in m.get("variation_endings", {}).items():
        if n > 3 and n > 0.08 * m["sentences"]:
            out.append(f"A15 '~{v}' 종결 {n}회: 평서 종결로 돌리거나 앞 문장과 이으세요")
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
