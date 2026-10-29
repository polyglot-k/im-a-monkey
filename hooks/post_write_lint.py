"""PostToolUse: 한글 .md/.html 쓰기 뒤 린트 결과를 알린다(막지 않음)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

MAX_BYTES = 200 * 1024


def main() -> None:
    import lint
    import visual
    from textutil import has_hangul

    data = json.load(sys.stdin)
    if data.get("tool_name") not in ("Write", "Edit", "MultiEdit"):
        return
    path = Path((data.get("tool_input") or {}).get("file_path") or "")
    if path.suffix.lower() not in (".md", ".html") or not path.is_file() or path.stat().st_size > MAX_BYTES:
        return
    text = path.read_text(encoding="utf-8")
    if not has_hangul(text):
        return
    found = lint.lint_text(text) + visual.check(text)
    if not found:
        return
    msg = f"[im-a-monkey] {path.name} 린트 {len(found)}건 (막지 않음, 고칠지 판단하세요)\n"
    msg += "\n".join(str(f) for f in found[:10])
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PostToolUse",
                                             "additionalContext": msg}}, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
