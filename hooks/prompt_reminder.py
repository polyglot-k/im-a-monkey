"""UserPromptSubmit: 한국어 프롬프트에만 짧은 리마인더."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))


def main() -> None:
    import config

    if config.load()["voice"] == "off":
        return
    prompt = json.load(sys.stdin).get("prompt") or ""
    if not re.search(r"[가-힣]", prompt):
        return
    text = (Path(__file__).resolve().parent.parent / "persona" / "reminder.md").read_text(encoding="utf-8").strip()
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "UserPromptSubmit",
                                             "additionalContext": text}}, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
