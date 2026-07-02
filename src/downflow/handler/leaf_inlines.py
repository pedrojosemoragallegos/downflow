from __future__ import annotations

from typing import Self, final

from downflow.action import Action

from .base import Handler


## INLINE-LEAF HANDLER
class LeafInline(Handler):
    def __init__(self) -> None:
        self._content: str = ""

    @property
    def content(self) -> str:
        return self._content


## Code Span Handler
@final
class CodeSpan(LeafInline):
    def __init__(self) -> None:
        super().__init__()
        self._opened: bool = False

    @classmethod
    def matches(cls, current: str, peek: str, /) -> Self | None:
        if current == "`":
            return cls()
        return None

    def __call__(self, current: str, peek: str, /) -> Action:
        if not self._opened:
            self._opened = True
            return Action.ADVANCE
        if current == "`":
            return Action.POP_AND_ADVANCE
        self._content += current
        return Action.ADVANCE


## Autolink Handler
@final
class AutoLink(LeafInline):
    def __init__(self) -> None:
        super().__init__()
        self._opened: bool = False

    @classmethod
    def matches(cls, current: str, peek: str, /) -> Self | None:
        if current == "<":
            return cls()
        return None

    def __call__(self, current: str, peek: str, /) -> Action:
        if not self._opened:
            self._opened = True
            return Action.ADVANCE
        if current == ">":
            return Action.POP_AND_ADVANCE
        self._content += current
        return Action.ADVANCE


## Raw HTML Handler
@final
class RawHTML(LeafInline):
    def __init__(self) -> None:
        super().__init__()
        self._opened: bool = False

    @classmethod
    def matches(cls, current: str, peek: str, /) -> Self | None:
        if current == "<":
            return cls()
        return None

    def __call__(self, current: str, peek: str, /) -> Action:
        if not self._opened:
            self._opened = True
            return Action.ADVANCE
        if current == ">":
            return Action.POP_AND_ADVANCE
        self._content += current
        return Action.ADVANCE


## Hardline Break Handler
@final
class HardlineBreak(LeafInline):
    @classmethod
    def matches(cls, current: str, peek: str, /) -> Self | None:
        if current == "\\" and peek == "\n":
            return cls()
        return None

    def __call__(self, current: str, peek: str, /) -> Action:
        if current == "\\":
            return Action.ADVANCE
        return Action.POP_AND_ADVANCE


## Softline Break Handler
@final
class SoftlineBreak(LeafInline):
    @classmethod
    def matches(cls, current: str, peek: str, /) -> Self | None:
        if current == "\n":
            return cls()
        return None

    def __call__(self, current: str, peek: str, /) -> Action:
        return Action.POP_AND_ADVANCE


## Textual Content Handler
@final
class Text(LeafInline):
    @classmethod
    def matches(cls, current: str, peek: str, /) -> Self | None:
        return cls()

    def __call__(self, current: str, peek: str, /) -> Action:
        self._content += current
        return Action.POP_AND_ADVANCE
