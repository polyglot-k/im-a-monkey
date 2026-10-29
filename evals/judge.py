"""기준선(플러그인 없음) 대 스킬(플러그인 있음) 쌍대 판정 도구."""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BEHAVIOR = ROOT / "evals" / "behavior"
RUNS = ROOT / "evals" / "runs"


def run_claude(prompt: str, plugin_dir: str | None) -> str:
    # 두 팔 모두 빈 임시 폴더에서, 프로젝트 설정만 읽고 MCP 없이 돌린다. 차이는 플러그인뿐이다.
    cmd = ["claude", "-p", prompt, "--setting-sources", "project", "--strict-mcp-config"]
    if plugin_dir:
        cmd += ["--plugin-dir", plugin_dir]
    r = subprocess.run(
        cmd, capture_output=True, text=True, timeout=300, cwd=tempfile.mkdtemp()
    )
    if r.returncode != 0:
        raise RuntimeError(f"claude 실패({r.returncode}): {r.stderr.strip()[:300]}")
    return r.stdout.strip()


def judge_prompt(rubric: str, first: str, second: str) -> str:
    return (
        "두 답변을 아래 기준만 보고 비교하세요. 답변 길이는 고려하지 마세요. "
        "순서도 품질과 무관합니다.\n\n"
        f"## 기준\n{rubric}\n\n## 첫째 답변\n{first}\n\n## 둘째 답변\n{second}\n\n"
        "기준에 더 잘 맞는 쪽의 이유를 짧게 쓰고, 마지막 줄에 "
        "`VERDICT: FIRST`, `VERDICT: SECOND`, `VERDICT: TIE` 중 하나만 쓰세요."
    )


def parse_verdict(output: str) -> str:
    found = re.findall(r"VERDICT:\s*(FIRST|SECOND|TIE)", output)
    return found[-1] if found else "TIE"


def combine(v_ab: str, v_ba: str) -> str:
    # A=기준선, B=스킬. AB에선 SECOND, BA에선 FIRST가 스킬 승.
    if v_ab == "SECOND" and v_ba == "FIRST":
        return "skill"
    if v_ab == "FIRST" and v_ba == "SECOND":
        return "baseline"
    return "tie"


def run_case(case: Path, out: Path) -> str:
    prompt = (case / "prompt.md").read_text(encoding="utf-8")
    rubric = (case / "rubric.md").read_text(encoding="utf-8")
    base = run_claude(prompt, None)
    skill = run_claude(prompt, str(ROOT))
    v_ab = parse_verdict(run_claude(judge_prompt(rubric, base, skill), None))
    v_ba = parse_verdict(run_claude(judge_prompt(rubric, skill, base), None))
    result = combine(v_ab, v_ba)
    out.mkdir(parents=True, exist_ok=True)
    (out / "baseline.md").write_text(base, encoding="utf-8")
    (out / "skill.md").write_text(skill, encoding="utf-8")
    (out / "verdict.json").write_text(
        json.dumps({"ab": v_ab, "ba": v_ba, "result": result}, ensure_ascii=False),
        encoding="utf-8",
    )
    return result


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("skill")
    ap.add_argument("--case")
    args = ap.parse_args()
    cases = sorted(p for p in (BEHAVIOR / args.skill).iterdir() if p.is_dir())
    if args.case:
        cases = [p for p in cases if p.name == args.case]
    stamp = datetime.now().strftime("%Y%m%d-%H%M")
    tally = {"skill": 0, "baseline": 0, "tie": 0}
    for case in cases:
        res = run_case(case, RUNS / stamp / args.skill / case.name)
        tally[res] += 1
        print(f"{case.name}: {res}")
    print(f"skill {tally['skill']} / baseline {tally['baseline']} / tie {tally['tie']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
