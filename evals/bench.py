"""한국어 글쓰기 플러그인 5개 팔 벤치마크. 사용법은 evals/bench/README.md."""
from __future__ import annotations

import argparse
import json
import os
import random
import re
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from preserve import compare  # noqa: E402  중립 diff(숫자·토큰·부정·링크·편집률)

CASES = ROOT / "evals" / "bench" / "cases"
BENCH = ROOT / ".superpowers" / "bench"
ARMS = {
    "baseline": None,
    "im-not-ai": "/Users/ably/.claude/plugins/cache/im-not-ai/humanize-korean/2.3.2",
    "im-not-strange-ai": str(BENCH / "src" / "im-not-strange-ai"),
    "patina": str(BENCH / "src" / "patina"),
    "im-a-monkey": str(ROOT),
}
REWRITE = "이 글을 사람이 쓴 것처럼 자연스럽게 다듬어 주세요. 다듬은 글만 주세요:\n\n"
TIMEOUT = 600


def load_case(path: Path) -> dict:
    raw = path.read_text(encoding="utf-8")
    _, head, body = raw.split("---\n", 2)
    meta = dict(line.split(": ", 1) for line in head.strip().splitlines())
    text = body.strip()
    prompt = REWRITE + text if meta["track"] == "A" else text
    return {"id": path.stem, "track": meta["track"], "intent": meta["intent"], "text": text, "prompt": prompt}


def run_claude(prompt: str, plugin_dir: str | None) -> dict:
    # judge.py와 같은 격리: 빈 임시 cwd, 프로젝트 설정만, MCP 없음. 프롬프트는 stdin으로(--allowedTools가 가변 인자라서).
    cmd = ["claude", "-p", "--setting-sources", "project", "--strict-mcp-config",
           "--output-format", "stream-json", "--verbose",
           "--allowedTools", "Read,Write,Edit,Bash(python3:*)"]
    if plugin_dir:
        cmd += ["--plugin-dir", plugin_dir, "--add-dir", plugin_dir]
    t0 = time.time()
    with tempfile.TemporaryDirectory() as cwd:
        r = subprocess.run(cmd, input=prompt, capture_output=True, text=True, timeout=TIMEOUT, cwd=cwd)
    out = {"tools": [], "plugins": [], "result": "", "error": None, "secs": round(time.time() - t0)}
    for line in r.stdout.splitlines():
        try:
            ev = json.loads(line)
        except json.JSONDecodeError:
            continue
        if ev.get("type") == "system" and ev.get("subtype") == "init":
            out["plugins"] = [p["name"] for p in ev.get("plugins", []) if p.get("path") != "builtin"]
        elif ev.get("type") == "assistant":
            for c in ev["message"].get("content", []):
                if c.get("type") == "tool_use":
                    inp = c.get("input", {})
                    detail = inp.get("skill") or inp.get("subagent_type") or inp.get("command") or inp.get("file_path") or ""
                    out["tools"].append(f"{c['name']}:{str(detail)[:80]}")
        elif ev.get("type") == "result":
            out["result"] = (ev.get("result") or "").strip()
            if ev.get("is_error"):
                out["error"] = f"is_error: {out['result'][:200]}"
    if r.returncode != 0 and not out["error"]:
        out["error"] = f"exit {r.returncode}: {r.stderr.strip()[:300]}"
    if not out["result"] and not out["error"]:
        out["error"] = "빈 결과"
    return out


# ---- humanize-scan 6신호 (im-not-ai humanize-scan SKILL.md를 정규식으로 옮김) ----
_CONNECTIVE_EXCLUDE = {"그리고", "그러면서", "그래서", "하지만", "그렇지만", "그러나", "그러고", "또한"}
_JEOK_NOUNS = {"목적", "흔적", "지적", "실적", "업적", "성적", "기적", "해적", "국적", "적"}


def _plain(s: str) -> str:
    s = re.sub(r"```.*?```", "", s, flags=re.S)
    s = re.sub(r"\]\([^)]*\)", "]", s)
    return re.sub(r"^[#>\-*\d.\s|]+", "", s, flags=re.M)


def _sentences(par: str) -> list[str]:
    return [x.strip() for x in re.split(r"(?<=[.!?])\s+|\n+", par) if len(x.strip()) > 1]


def _ending(s: str, n: int) -> str:
    h = re.sub(r"[^가-힣]", "", s)
    return h[-n:]


def _max_run(xs: list[str]) -> int:
    best = cur = 0
    for i, x in enumerate(xs):
        cur = cur + 1 if i and x == xs[i - 1] else 1
        best = max(best, cur)
    return best


def signals(text: str) -> dict:
    t = _plain(text)
    pars = [p for p in re.split(r"\n\s*\n", t) if p.strip()]
    sents = [s for p in pars for s in _sentences(p)]
    c8 = len(re.findall(r"아니라|아닌,|인가,[^.?!]*인가", t))
    long_share = sum(len(s) >= 100 for s in sents) / len(sents) if sents else 0
    c11 = [m.group(0) for m in re.finditer(r"([가-힣]+(?:고|며|지만|면서|아서|어서|해서|여서|워서)),", t)
           if m.group(1) not in _CONNECTIVE_EXCLUDE]
    i4 = sum(bool(re.search(r"야\s*(한다|합니다|해요|하죠|돼요|된다|됩니다|할 것)", (_sentences(p) or [""])[-1]))
             for p in pars)
    run2 = _max_run([_ending(s, 2) for s in sents])
    run1 = _max_run([_ending(s, 1) for s in sents])
    f5 = [w for w in re.findall(r"([가-힣]+적) [가-힣]", t) if w not in _JEOK_NOUNS]
    fired = {
        "C-8": c8 >= 2,
        "E-1": len(sents) >= 4 and long_share < 0.1,  # ponytail: "거의 없음"을 10% 미만으로 정함
        "C-11": len(c11) >= 1,
        "I-4": i4 >= 2,
        "E-2": run2 >= 4,
        "F-5": len(f5) >= 3,
    }
    return {"fired": sum(fired.values()), "which": [k for k, v in fired.items() if v],
            "c8": c8, "long_share": round(long_share, 2), "c11": len(c11), "i4": i4,
            "run2": run2, "run1": run1, "f5": len(f5)}


# ---- 블라인드 순위 ----
def judge_prompt(case: dict, cands: list[str]) -> str:
    task = "원문을 사람이 쓴 것처럼 다듬는 과제" if case["track"] == "A" else "아래 요청에 답하는 과제"
    body = "\n\n".join(f"## 후보 {chr(65 + i)}\n{c}" for i, c in enumerate(cands))
    return (
        f"다음은 {task}에 대한 답 다섯 개예요. 기준의 우선순위대로 1위부터 5위까지 매기세요.\n"
        "1. 의미 보존(가장 중요): 사실·숫자·부정·조건을 바꾸거나 빼거나 지어내지 않았는가\n"
        "2. 사람이 쓴 것 같은 한국어인가\n3. 읽기 쉬운가\n4. 불필요한 변경이 없는가\n"
        "길이는 장점이 아니에요. 후보 순서는 품질과 무관해요.\n\n"
        f"## 원문/요청\n{case['prompt']}\n\n{body}\n\n"
        "이유를 짧게 쓰고, 마지막 줄에 `RANKING: C > A > E > B > D`처럼 다섯 글자를 모두 한 번씩 쓰세요."
    )


def parse_ranking(s: str, n: int) -> list[int] | None:
    found = re.findall(r"RANKING:\s*([A-E](?:\s*>\s*[A-E])+)", s)
    if not found:
        return None
    order = [ord(x) - 65 for x in re.findall(r"[A-E]", found[-1])]
    return order if sorted(order) == list(range(n)) else None


def rank_case(case: dict, outs: dict, rdir: Path, seed: int) -> dict:
    arms = [a for a in ARMS if outs.get(a)]  # ERROR 팔은 순위에서 뺀다
    ranks: dict[str, list[int]] = {a: [] for a in arms}
    for k in range(2):
        f = rdir / f"judge-{k}.json"
        if f.exists():
            saved = json.loads(f.read_text(encoding="utf-8"))
        else:
            order = arms[:]
            random.Random(seed * 10 + k).shuffle(order)
            saved = {"order": order, "ranking": None, "raw": ""}
            for _ in range(2):  # 못 읽으면 한 번 다시
                try:
                    res = run_claude(judge_prompt(case, [outs[a] for a in order]), None)
                except subprocess.TimeoutExpired:
                    continue
                saved["raw"] = res["result"]
                saved["ranking"] = parse_ranking(res["result"], len(order))
                if saved["ranking"]:
                    break
            f.write_text(json.dumps(saved, ensure_ascii=False, indent=1), encoding="utf-8")
        if saved["ranking"]:
            for pos, idx in enumerate(saved["ranking"]):
                ranks[saved["order"][idx]].append(pos + 1)
    return {a: (sum(v) / len(v) if v else None) for a, v in ranks.items()}


def generate(job: tuple) -> None:
    case, arm, rdir = job
    f = rdir / f"{arm}.json"
    if f.exists():
        return
    try:
        res = run_claude(case["prompt"], ARMS[arm])
    except subprocess.TimeoutExpired:
        res = {"error": f"timeout {TIMEOUT}s", "result": "", "tools": [], "plugins": []}
    (rdir / f"{arm}.md").write_text(res["result"], encoding="utf-8")
    f.write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{case['id']} {arm}: {'ERROR ' + res['error'] if res['error'] else 'ok'} ({res.get('secs')}s)", flush=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(BENCH / "runs" / time.strftime("%Y%m%d-%H%M")),
                    help="결과 폴더. 같은 폴더를 다시 주면 끝난 칸은 건너뛰어요")
    ap.add_argument("--jobs", type=int, default=5)
    args = ap.parse_args()
    out = Path(args.out)
    cases = [load_case(p) for p in sorted(CASES.glob("*.md"))]
    jobs = []
    for c in cases:
        (out / c["id"]).mkdir(parents=True, exist_ok=True)
        (out / c["id"] / "input.md").write_text(c["text"], encoding="utf-8")
        jobs += [(c, a, out / c["id"]) for a in ARMS]
    with ThreadPoolExecutor(args.jobs) as ex:
        list(ex.map(generate, jobs))

    summary, all_outs = {}, {}
    for c in cases:
        rdir = out / c["id"]
        outs, row = {}, {}
        for a in ARMS:
            meta = json.loads((rdir / f"{a}.json").read_text(encoding="utf-8"))
            text = meta["result"] if not meta["error"] else ""
            outs[a] = text
            cell = {"error": meta["error"], "tools": meta["tools"], "plugins": meta["plugins"], "secs": meta.get("secs")}
            if text:
                cell["signals"] = signals(text)
                cell["len_ratio"] = round(len(text.strip()) / len(c["text"]), 2)
                if c["track"] == "A":
                    cell["preserve"] = compare(c["text"], text)
            row[a] = cell
        row["_input_signals"] = signals(c["text"])
        summary[c["id"]], all_outs[c["id"]] = row, outs
    with ThreadPoolExecutor(args.jobs) as ex:
        avgs = list(ex.map(lambda ic: rank_case(ic[1], all_outs[ic[1]["id"]], out / ic[1]["id"], ic[0]),
                           enumerate(cases)))
    for c, avg in zip(cases, avgs):
        for a, r in avg.items():
            summary[c["id"]][a]["rank"] = r
        print(c["id"], avg, flush=True)
    (out / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"요약: {out / 'summary.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
