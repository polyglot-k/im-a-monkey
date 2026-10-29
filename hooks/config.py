"""im-a-monkey 사용자 설정. 표준 라이브러리만 쓴다."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

VOICES = ("haeyo", "banmal", "hapnida", "off")
DEFAULT = {"voice": "haeyo"}


def config_dir() -> Path:
    xdg = os.environ.get("XDG_CONFIG_HOME")
    base = Path(xdg) if xdg else Path.home() / ".config"
    return base / "im-a-monkey"


def load() -> dict:
    cfg = dict(DEFAULT)
    try:
        data = json.loads((config_dir() / "config.json").read_text(encoding="utf-8"))
        if isinstance(data, dict) and data.get("voice") in VOICES:
            cfg["voice"] = data["voice"]
    except Exception:
        pass
    env = os.environ.get("IM_A_MONKEY_VOICE")
    if env in VOICES:
        cfg["voice"] = env
    return cfg


def save(cfg: dict) -> None:
    d = config_dir()
    d.mkdir(parents=True, exist_ok=True)
    (d / "config.json").write_text(json.dumps(cfg, ensure_ascii=False) + "\n", encoding="utf-8")


def main(argv: list) -> int:
    if argv[:1] == ["get"]:
        print(load()["voice"])
        return 0
    if len(argv) == 2 and argv[0] == "set" and argv[1] in VOICES:
        save({**load(), "voice": argv[1]})
        print(f"voice={argv[1]}")
        return 0
    print("사용법: config.py get | set <haeyo|banmal|hapnida|off>", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
