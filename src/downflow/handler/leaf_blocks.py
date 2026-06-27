from __future__ import annotations

from typing import Self, final

from downflow.action import Action

from .base import Handler


## LEAF-BLOCK HANDLER
class LeafBlock(Handler): ...


## Thematic Break Handler
@final
class ThematicBreak(LeafBlock):
    @classmethod
    def matches(cls, current: str, peek: str, /) -> Self | None:
        if current.startswith("---"):
            return cls()

        return None

    def __call__(self, current: str, peek: str, /) -> Action:
        return Action.ADVANCE


## ATX Heading Handler
@final
class ATXHeading(LeafBlock):
    @classmethod
    def matches(cls, current: str, peek: str, /) -> Self | None:
        if current.startswith("#"):
            return cls()

        return None

    def __call__(self, current: str, peek: str, /) -> Action:
        return Action.ADVANCE


## Indented Code Block Handler
@final
class IndentedCodeBlock(LeafBlock):
    @classmethod
    def matches(cls, current: str, peek: str, /) -> Self | None:
        if current.startswith("    "):
            return cls()

        return None

    def __call__(self, current: str, peek: str, /) -> Action:
        return Action.ADVANCE


## Fenced Code Block Handler
@final
class FencedCodeBlock(LeafBlock):
    @classmethod
    def matches(cls, current: str, peek: str, /) -> Self | None:
        if current.startswith("```"):
            return cls()

        return None

    def __call__(self, current: str, peek: str, /) -> Action:
        return Action.ADVANCE


## HTML Block Handler
@final
class HTMLBlock(LeafBlock):
    @classmethod
    def matches(cls, current: str, peek: str, /) -> Self | None:
        if current.startswith("<"):
            return cls()

        return None

    def __call__(self, current: str, peek: str, /) -> Action:
        return Action.ADVANCE


## Link Reference Definition Handler
@final
class LinkReferenceDefinition(LeafBlock):
    @classmethod
    def matches(cls, current: str, peek: str, /) -> Self | None:
        if current.startswith("["):
            return cls()

        return None

    def __call__(self, current: str, peek: str, /) -> Action:
        return Action.ADVANCE


## Paragraph Handler
@final
class Paragraph(LeafBlock):
    @classmethod
    def matches(cls, current: str, peek: str, /) -> Self | None:
        if current.strip():
            return cls()

        return None

    def __call__(self, current: str, peek: str, /) -> Action:
        if current == "\n":
            return Action.POP

        return Action.ADVANCE
