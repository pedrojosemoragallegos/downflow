from __future__ import annotations

from typing import Self, final

from downflow.action import Action

from .base import Handler


## CONTAINER-BLOCK HANDLER
class ContainerBlock(Handler): ...


## INLINE-CONTAINER-BLOCK HANDLER (children are inline nodes)
class InlineContainerBlock(ContainerBlock): ...


## Blockquote Handler
@final
class Blockquote(ContainerBlock):
    def __init__(self) -> None:
        self._at_line_start: bool = True

    @classmethod
    def matches(cls, current: str, peek: str, /) -> Self | None:  # noqa: ARG003
        if current == ">":
            return cls()

        return None

    def __call__(self, current: str, peek: str, /) -> Action:
        if current == ">" and self._at_line_start:
            # Consume the continuation marker at the start of a line.
            self._at_line_start = False
            return Action.ADVANCE

        if current == " " and not self._at_line_start:
            # Consume the optional space after ">".
            return Action.ADVANCE

        if current == "\n":
            if peek == "\n":
                return Action.POP
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
    def __init__(self) -> None:
        self._at_line_start: bool = True

    @classmethod
    def matches(cls, current: str, peek: str, /) -> Self | None:
        if current == "-" and peek == " ":
            return cls()

        return None

    def __call__(self, current: str, peek: str, /) -> Action:
        if current == "\n":
            self._at_line_start = True
            return Action.ADVANCE
        if self._at_line_start:
            if current == "-" and peek == " ":
                self._at_line_start = False
                return Action.DELEGATE
            return Action.POP
        return Action.DELEGATE


## ListItem Handler
@final
class ListItem(ContainerBlock):
    def __init__(self) -> None:
        self._skip_count: int = 0

    @classmethod
    def matches(cls, current: str, peek: str, /) -> Self | None:
        if current == "-" and peek == " ":
            return cls()

        return None

    def __call__(self, current: str, peek: str, /) -> Action:
        if self._skip_count < 2:
            self._skip_count += 1
            return Action.ADVANCE
        if current == "\n":
            return Action.POP
        return Action.DELEGATE


## OrderedListItem Handler
@final
class OrderedListItem(ContainerBlock):
    def __init__(self) -> None:
        self._past_marker: bool = False

    @classmethod
    def matches(cls, current: str, peek: str, /) -> Self | None:
        if current.isdigit() and peek == ".":
            return cls()

        return None

    def __call__(self, current: str, peek: str, /) -> Action:
        if not self._past_marker:
            if current in "0123456789.":
                return Action.ADVANCE
            if current == " ":
                self._past_marker = True
                return Action.ADVANCE
        if current == "\n":
            return Action.POP
        return Action.DELEGATE
