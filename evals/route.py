"""routing.md의 모호한 요청마다 어떤 monkey 스킬을 고르는지 claude -p로 재서 정확도를 낸다."""
from __future__ import annotations

import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SUFFIX = "\n\n작업은 하지 말고, 이 요청에 쓸 im-a-monkey 스킬 이름 하나만 마지막 줄에 적어줘."


def parse_skill(out: str) -> str:
    """마지막 줄에서 monkey[-a-z]* 이름을 뽑는다. 없으면 빈 문자열."""
    lines = [ln for ln in out.strip().splitlines() if ln.strip()]
    m = re.findall(r"monkey[-a-z]*", lines[-1]) if lines else []
    return m[-1] if m else ""


def parse_rows(text: str) -> list[tuple[str, str]]:
    rows = []
    for ln in text.splitlines():
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        if len(cells) >= 2 and cells[1].startswith("monkey"):
            rows.append((cells[0], cells[1]))
    return rows


def route(req: str) -> str:
    cmd = ["claude", "-p", "--plugin-dir", str(ROOT), "--setting-sources", "project", "--strict-mcp-config"]
    with tempfile.TemporaryDirectory() as cwd, tempfile.TemporaryDirectory() as xdg:
        env = dict(os.environ, XDG_CONFIG_HOME=xdg)
        r = subprocess.run(cmd, input=req + SUFFIX, capture_output=True, text=True, timeout=300, cwd=cwd, env=env)
    return parse_skill(r.stdout)


def main(path: str) -> None:
    rows = parse_rows(Path(path).read_text(encoding="utf-8"))
    hit = 0
    print("| 요청 | 기대 | 실제 | 일치 |\n|---|---|---|---|")
    for req, want in rows:
        try:
            got = route(req)
        except (subprocess.TimeoutExpired, OSError):
            got = ""
        hit += got == want
        print(f"| {req[:30]} | {want} | {got or '-'} | {'예' if got == want else '아니오'} |", flush=True)
    print(f"\n{hit}/{len(rows)} 일치 ({hit * 100 // max(len(rows), 1)}%)")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else str(ROOT / "evals" / "routing.md"))
