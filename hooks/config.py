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


def _file() -> dict:
    try:
        data = json.loads((config_dir() / "config.json").read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def load() -> dict:
    cfg = dict(DEFAULT)
    if _file().get("voice") in VOICES:
        cfg["voice"] = _file()["voice"]
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
    if argv[:1] == ["path"]:
        print(config_dir())
        return 0
    if len(argv) == 2 and argv[0] == "set" and argv[1] in VOICES:
        save({**_file(), "voice": argv[1]})  # 환경변수 값은 파일에 새기지 않는다
        print(f"voice={argv[1]}")
        return 0
    print("사용법: config.py get | path | set <haeyo|banmal|hapnida|off>", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
