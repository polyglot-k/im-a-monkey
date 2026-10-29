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
_FENCE_LINE = re.compile(r"[ \t]*(`{3,}|~{3,})(.*)")
_COMMENT = re.compile(r"<!--(?!\s*visual:).*?-->", re.S)
_INLINE = re.compile(r"(`+)(?!`).+?(?<!`)\1(?!`)")


def _blank(m: re.Match) -> str:
    return "".join("\n" if c == "\n" else " " for c in m.group(0))


def fence_spans(text: str) -> list[tuple[int, int, str]]:
    """최상위 코드 펜스의 (시작, 끝, info). 닫는 펜스는 같은 문자·같거나 긴 길이·뒤에 공백만(CommonMark)."""
    out, pos, open_ = [], 0, None
    for ln in text.split("\n"):
        end = pos + len(ln)
        m = _FENCE_LINE.fullmatch(ln)
        if open_ is None:
            if m and not (m.group(1)[0] == "`" and "`" in m.group(2)):
                open_ = (pos, m.group(1), m.group(2).strip())
        elif m and m.group(1)[0] == open_[1][0] and len(m.group(1)) >= len(open_[1]) and not m.group(2).strip():
            out.append((open_[0], end, open_[2]))
            open_ = None
        pos = end + 1
    if open_:
        out.append((open_[0], len(text), open_[2]))
    return out


def _blank_str(t: str) -> str:
    return "".join("\n" if c == "\n" else " " for c in t)


def strip_ignored(text: str) -> str:
    """무시 구간을 같은 길이의 공백으로 바꾼다(줄바꿈 유지)."""
    text = text.replace("\r\n", "\n")
    # off/on 구간을 먼저 지워야 그 안의 펜스·주석이 바깥 구조를 깨지 못한다.
    text = _OFF_ON.sub(_blank, text)
    for a, b, _ in fence_spans(text):
        text = text[:a] + _blank_str(text[a:b]) + text[b:]
    # 인라인 코드를 주석보다 먼저: `<!--`가 이어지는 글을 지우지 않게 한다.
    for pat in (_INLINE, _COMMENT):
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
