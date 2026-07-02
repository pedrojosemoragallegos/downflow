from __future__ import annotations

from typing import Self, final

from downflow.action import Action

from .base import Handler
from .container_blocks import InlineContainerBlock


## LEAF-BLOCK HANDLER
class LeafBlock(Handler):
    def __init__(self) -> None:
        self._content: str = ""

    @property
    def content(self) -> str:
        return self._content


## Thematic Break Handler
@final
class ThematicBreak(LeafBlock):
    def __init__(self) -> None:
        super().__init__()
        self._count: int = 0

    @classmethod
    def matches(cls, current: str, peek: str, /) -> Self | None:
        if current == "-" and peek == "-":
            return cls()

        return None

    def __call__(self, current: str, peek: str, /) -> Action:
        if current == "-":
            self._count += 1
            return Action.ADVANCE
        if current == "\n":
            return Action.POP
        return Action.ADVANCE


## ATX Heading Handler
@final
class ATXHeading(LeafBlock):
    def __init__(self) -> None:
        super().__init__()
        self._level: int = 0
        self._past_marker: bool = False

    @classmethod
    def matches(cls, current: str, peek: str, /) -> Self | None:
        if current == "#":
            return cls()

        return None

    def __call__(self, current: str, peek: str, /) -> Action:
        if current == "#" and not self._past_marker:
            self._level += 1
            return Action.ADVANCE
        if current == " " and not self._past_marker:
            self._past_marker = True
            return Action.ADVANCE
        if current == "\n":
            return Action.POP
        self._past_marker = True
        self._content += current
        return Action.ADVANCE


## Indented Code Block Handler
@final
class IndentedCodeBlock(LeafBlock):
    def __init__(self) -> None:
        super().__init__()
        self._indent: int = 0

    @classmethod
    def matches(cls, current: str, peek: str, /) -> Self | None:
        if current == " " and peek == " ":
            return cls()

        return None

    def __call__(self, current: str, peek: str, /) -> Action:
        if current == " " and self._indent < 4:
            self._indent += 1
            return Action.ADVANCE
        if current == "\n":
            return Action.POP
        self._content += current
        return Action.ADVANCE


## Fenced Code Block Handler
@final
class FencedCodeBlock(LeafBlock):
    def __init__(self) -> None:
        super().__init__()
        self._fence_consumed: bool = False
        self._at_line_start: bool = False
        self._closing_count: int = 0

    @classmethod
    def matches(cls, current: str, peek: str, /) -> Self | None:
        if current == "`" and peek == "`":
            return cls()

        return None

    def __call__(self, current: str, peek: str, /) -> Action:
        if not self._fence_consumed:
            if current == "\n":
                self._fence_consumed = True
                self._at_line_start = True
            return Action.ADVANCE
        if current == "\n":
            self._at_line_start = True
            self._closing_count = 0
            self._content += current
            return Action.ADVANCE
        if self._at_line_start and current == "`":
            self._closing_count += 1
            if self._closing_count >= 3:
                return Action.POP_AND_ADVANCE
            return Action.ADVANCE
        self._at_line_start = False
        self._closing_count = 0
        self._content += current
        return Action.ADVANCE


## HTML Block Handler
@final
class HTMLBlock(LeafBlock):
    @classmethod
    def matches(cls, current: str, peek: str, /) -> Self | None:
        if current == "<" and peek in ("!", "?", "/"):
            return cls()

        return None

    def __call__(self, current: str, peek: str, /) -> Action:
        if current == "\n" and peek == "\n":
            return Action.POP
        self._content += current
        return Action.ADVANCE


## Link Reference Definition Handler
@final
class LinkReferenceDefinition(LeafBlock):
    @classmethod
    def matches(cls, current: str, peek: str, /) -> Self | None:
        if current == "[":
            return cls()

        return None

    def __call__(self, current: str, peek: str, /) -> Action:
        self._content += current
        return Action.ADVANCE


## Paragraph Handler
@final
class Paragraph(InlineContainerBlock):
    @classmethod
    def matches(cls, current: str, peek: str, /) -> Self | None:
        if current in (" ", "\t", "\n", "\r"):
            return None
        return cls()

    def __call__(self, current: str, peek: str, /) -> Action:
        if current == "\n" and peek == "\n":
            return Action.POP
        return Action.DELEGATE
