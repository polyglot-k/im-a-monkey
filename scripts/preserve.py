"""im-a-monkey 의미 보존 대조. 사용: python3 scripts/preserve.py ORIGINAL REVISED [--json]"""
from __future__ import annotations

import argparse
import difflib
import json
import re
import sys
from collections import Counter

_NUM = re.compile(r"\d[\d,.]*%?")
_TOK = re.compile(r"[A-Za-z_][A-Za-z0-9_.\-/]*")
_NEG = re.compile(r"안\s|않|못|없|아니")
_LINK = re.compile(r"\]\(([^)\s]+)\)")
_QUOTE = re.compile(r"\"[^\"\n]+\"|“[^”\n]+”")


def _missing(a: list[str], b: list[str]) -> list[str]:
    """a에서 b에 없는 항목(다중 집합), a의 순서 유지."""
    left = Counter(b)
    out = []
    for x in a:
        if left[x] > 0:
            left[x] -= 1
        else:
            out.append(x)
    return out


def _nums(s: str) -> list[str]:
    # 문장 끝 마침표·쉼표는 숫자의 일부가 아니다
    return [n.rstrip(".,") for n in _NUM.findall(s)]


def _toks(s: str) -> list[str]:
    # 문장 끝 마침표 등 꼬리 구두점은 토큰의 일부가 아니다
    return [t.rstrip(".-/") for t in _TOK.findall(s)]


def _links(s: str) -> list[str]:
    return _LINK.findall(s) + _QUOTE.findall(s)


def compare(original: str, revised: str) -> dict:
    o = original.replace("\r\n", "\n")
    r = revised.replace("\r\n", "\n")
    res = {
        "missing_numbers": _missing(_nums(o), _nums(r)),
        "missing_tokens": _missing(_toks(o), _toks(r)),
        "negation_delta": len(_NEG.findall(r)) - len(_NEG.findall(o)),
        "missing_links": _missing(_links(o), _links(r)),
        "edit_rate": round(1 - difflib.SequenceMatcher(None, o.split(), r.split()).ratio(), 2),
    }
    res["ok"] = not (res["missing_numbers"] or res["missing_tokens"]
                     or res["negation_delta"] or res["missing_links"])
    return res


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("original")
    ap.add_argument("revised")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    with open(args.original, encoding="utf-8") as f:
        a = f.read()
    with open(args.revised, encoding="utf-8") as f:
        b = f.read()
    res = compare(a, b)
    if args.json:
        print(json.dumps(res, ensure_ascii=False))
    else:
        for k, v in res.items():
            print(f"{k}: {v}")
    return 0 if res["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
