"""SessionStart: 페르소나 주입."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))


def main() -> None:
    import config

    voice = config.load()["voice"]
    if voice == "off":
        return
    core = (Path(__file__).resolve().parent.parent / "persona" / "core.md").read_text(encoding="utf-8")
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "SessionStart",
                                             "additionalContext": f"{core}\n말투: {voice}"}}, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
