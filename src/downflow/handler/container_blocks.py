from __future__ import annotations

from typing import Self, final

from downflow.action import Action

from .base import Handler


## CONTAINER-BLOCK HANDLER
class ContainerBlock(Handler): ...


## Blockquote Handler
@final
class Blockquote(ContainerBlock):
    def __init__(self) -> None:
        self._at_line_start: bool = True

    @classmethod
    def matches(cls, current: str, peek: str, /) -> Self | None:  # noqa: ARG003
        if current == ">":
            print("MATCHED BLOCKQUOTE")
            return cls()

        return None

    def __call__(self, current: str, peek: str, /) -> Action:  # noqa: ARG002
        if current == ">":
            # Consume the blockquote marker.
            self._at_line_start = False
            return Action.ADVANCE

        if current == "\n":
            # Stay inside the blockquote until the next line proves otherwise.
            self._at_line_start = True
            return Action.ADVANCE

        if self._at_line_start:
            # We are at the start of a new line, but there is no ">".
            # The blockquote is done. Do not consume this character.
            return Action.POP

        return Action.DELEGATE


## List Handler
@final
class List(ContainerBlock):
    @classmethod
    def matches(cls, current: str, peek: str, /) -> Self | None:
        if current.startswith("- "):
            return cls()

        return None

    def __call__(self, current: str, peek: str, /) -> Action:
        return Action.ADVANCE


## ListItem Handler
@final
class ListItem(ContainerBlock):
    @classmethod
    def matches(cls, current: str, peek: str, /) -> Self | None:
        if current.startswith("- "):
            return cls()

        return None

    def __call__(self, current: str, peek: str, /) -> Action:
        return Action.ADVANCE
