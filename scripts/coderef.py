"""im-a-monkey 코드 참조 검증. 사용: python3 scripts/coderef.py FILE --repo PATH [--json]"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from textutil import Finding, line_col, strip_blocks  # noqa: E402

_SHA = r"[0-9a-f]{7,40}"
_LINK = re.compile(
    rf"\[((?:`[^`\n]*`|[^\]\n`])*)\]\(https://github\.com/[^/\s)]+/[^/\s)]+/blob/({_SHA})/([^)#\s]+)#L(\d+)(?:-L(\d+))?\)")
_TICK = re.compile(rf"`([^`\s:]+):(\d+)(?:-(\d+))?@({_SHA})`")
_SYMBOL = re.compile(r"`([\w.]+)(?:\(\))?`")


def _show(repo: str, sha: str, path: str) -> list[str] | None:
    r = subprocess.run(["git", "-C", repo, "show", f"{sha}:{path}"], capture_output=True)
    if r.returncode != 0:
        return None
    return r.stdout.decode("utf-8", "replace").splitlines()


def check(text: str, repo: str) -> list[Finding]:
    text = text.replace("\r\n", "\n")
    s = strip_blocks(text)  # 펜스·off 구간 안의 예시 참조는 검사하지 않는다(같은 길이라 위치는 그대로)
    refs = [(m.start(), m.group(2), m.group(3), int(m.group(4)), int(m.group(5) or m.group(4)), m.group(1))
            for m in _LINK.finditer(s)]
    refs += [(m.start(), m.group(4), m.group(1), int(m.group(2)), int(m.group(3) or m.group(2)), "")
             for m in _TICK.finditer(s)]
    found = []
    for pos, sha, path, a, b, label in refs:
        line, col = line_col(text, pos)
        ex = text[pos:pos + 60].split("\n")[0]

        def bad(msg: str) -> None:
            found.append(Finding("T04", line, col, ex, msg))

        lines = _show(repo, sha, path)
        if lines is None:
            bad("커밋이나 경로가 없다")
        elif a < 1 or b < a or b > len(lines):
            bad("줄 범위 밖")
        else:
            sym = _SYMBOL.search(label)
            if sym:
                name = sym.group(1).rsplit(".", 1)[-1]
                if name not in "\n".join(lines[a - 1:b]):
                    bad(f"그 줄에 {name}가 없다")
    return sorted(found, key=lambda f: (f.line, f.col))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("file")
    ap.add_argument("--repo", required=True)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    with open(a.file, encoding="utf-8", newline="") as f:
        try:
            found = check(f.read(), a.repo)
        except FileNotFoundError:
            print("coderef: git을 실행할 수 없어요. git을 설치하고 PATH에 있는지 확인하세요.", file=sys.stderr)
            return 2
    if a.json:
        print(json.dumps([f.__dict__ for f in found], ensure_ascii=False))
    else:
        for f in found:
            print(f)
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
