"""monkey-human용 한 번에 점검. 임시 파일 없이 stdin으로 받는다.

scan:    원문을 stdin으로 → 린트·리듬 결과
compare: 원문, 구분선 '=====REVISED=====', 고친 글을 stdin으로 → 전후 린트·리듬 + 의미 보존
"""
from __future__ import annotations

import json
import re
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lint import lint_text  # noqa: E402
from preserve import compare  # noqa: E402
from rhythm import flags, measure, split_sentences  # noqa: E402

SEP = "=====REVISED====="


def check(text: str) -> dict:
    found = lint_text(text)
    return {
        "lint_count": len(found),
        "by_id": dict(Counter(f.id for f in found)),
        "lint": [{"id": f.id, "line": f.line, "excerpt": f.excerpt} for f in found],
        "rhythm_flags": flags(measure(text)),
    }


def _register(sentence: str) -> str | None:
    end = re.sub(r"[\s.!?)\]\"'”’]+$", "", sentence)
    if re.search(r"(니다|니까|습니까)$", end):
        return "합니다체"
    if end.endswith(("요", "죠")):  # 죠는 지요의 준말이라 해요체다
        return "해요체"
    return None


def register_mixed(orig: str, rev: str) -> list[str]:
    """원문에 거의 없던 말투(10% 미만)가 고친 글에 새로 생기면 알린다."""
    def counts(t: str) -> Counter:
        return Counter(r for r in map(_register, split_sentences(t)) if r)
    before, after = counts(orig), counts(rev)
    total = sum(before.values()) or 1
    return [f"{reg} {n - before.get(reg, 0)}문장" for reg, n in after.items()
            if before.get(reg, 0) / total < 0.1 and n > before.get(reg, 0)]


def run(mode: str, data: str) -> dict:
    if mode == "scan":
        return check(data)
    if SEP not in data:
        raise ValueError(f"compare는 원문과 고친 글 사이에 '{SEP}' 줄이 필요해요")
    orig, rev = (part.strip("\n") for part in data.split(SEP, 1))
    after = check(rev)
    after.pop("lint")
    before = check(orig)
    before.pop("lint")
    return {"before": before, "after": after, "preserve": compare(orig, rev),
            "register_mixed": register_mixed(orig, rev)}


def main() -> int:
    if len(sys.argv) != 2 or sys.argv[1] not in ("scan", "compare"):
        print("사용법: human_check.py scan|compare < 입력", file=sys.stderr)
        return 2
    try:
        out = run(sys.argv[1], sys.stdin.read())
    except ValueError as e:
        print(e, file=sys.stderr)
        return 2
    print(json.dumps(out, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
