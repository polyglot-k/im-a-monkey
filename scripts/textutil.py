"""im-a-monkey 공통 텍스트 유틸. 표준 라이브러리만 쓴다."""
from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Finding:
    id: str
    line: int
    col: int
    excerpt: str
    message: str

    def __str__(self) -> str:
        return f"{self.line}:{self.col} {self.id} {self.message} | {self.excerpt}"


_OFF_ON = re.compile(r"<!--\s*monkey-lint:\s*off\s*-->.*?(?:<!--\s*monkey-lint:\s*on\s*-->|\Z)", re.S)
_FENCE = re.compile(r"^[ \t]*(```|~~~).*?(?:^[ \t]*\1[^\n]*$|\Z)", re.S | re.M)
_COMMENT = re.compile(r"<!--(?!\s*visual:).*?-->", re.S)
_INLINE = re.compile(r"(`+)(?!`).+?(?<!`)\1(?!`)")


def _blank(m: re.Match) -> str:
    return "".join("\n" if c == "\n" else " " for c in m.group(0))


def strip_ignored(text: str) -> str:
    """무시 구간을 같은 길이의 공백으로 바꾼다(줄바꿈 유지)."""
    text = text.replace("\r\n", "\n")
    # off/on 구간을 먼저 지워야 그 안의 펜스·주석이 바깥 구조를 깨지 못한다.
    for pat in (_OFF_ON, _FENCE, _COMMENT, _INLINE):
        text = pat.sub(_blank, text)
    return text


def line_col(text: str, offset: int) -> tuple[int, int]:
    head = text[:offset]
    return head.count("\n") + 1, offset - (head.rfind("\n") + 1) + 1


def has_hangul(text: str, min_chars: int = 20) -> bool:
    return len(re.findall(r"[가-힣]", text)) >= min_chars


def eojeol_count(text: str) -> int:
    return len(text.split())


def catalog_ids(path: str) -> set[str]:
    with open(path, encoding="utf-8") as f:
        return set(re.findall(r"^### ([A-Z]\d{2}) ", f.read(), re.M))
