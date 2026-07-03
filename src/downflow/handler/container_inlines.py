from __future__ import annotations

from typing import Self, final

from downflow.action import Action

from .base import Handler


## INLINE-CONTAINER HANDLER
class ContainerInline(Handler): ...


## Emphasis Handler
@final
class Emphasis(ContainerInline):
    def __init__(self) -> None:
        self._opened: bool = False

    @classmethod
    def matches(cls, current: str, peek: str, /) -> Self | None:
        if current == "*" and peek != "*":
            return cls()

        return None

    def __call__(self, current: str, peek: str, /) -> Action:
        if not self._opened:
            self._opened = True
            return Action.ADVANCE
        if current == "*":
            return Action.POP_AND_ADVANCE
        return Action.DELEGATE


## Strong Emphasis Handler
@final
class StrongEmphasis(ContainerInline):
    def __init__(self) -> None:
        self._opener_count: int = 0
        self._closer_started: bool = False

    @classmethod
    def matches(cls, current: str, peek: str, /) -> Self | None:
        if current == "*" and peek == "*":
            return cls()

        return None

    def __call__(self, current: str, peek: str, /) -> Action:
        if self._opener_count < 2:
            self._opener_count += 1
            return Action.ADVANCE
        if current == "*":
            if self._closer_started:
                return Action.POP_AND_ADVANCE
            if peek == "*":
                self._closer_started = True
                return Action.ADVANCE
            return Action.DELEGATE
        self._closer_started = False
        return Action.DELEGATE


## Link Handler
@final
class Link(ContainerInline):
    def __init__(self) -> None:
        self._opened: bool = False
        self._closing: bool = False
        self._url_open: bool = False
        self._url: str = ""

    @property
    def url(self) -> str:
        return self._url

    @classmethod
    def matches(cls, current: str, peek: str, /) -> Self | None:
        if current == "[":
            return cls()

        return None

    def __call__(self, current: str, peek: str, /) -> Action:
        if not self._opened:
            self._opened = True
            return Action.ADVANCE
        if self._closing:
            if not self._url_open:
                if current == "(":
                    self._url_open = True
                    return Action.ADVANCE
                return Action.POP
            if current == ")":
                return Action.POP_AND_ADVANCE
            self._url += current
            return Action.ADVANCE
        if current == "]":
            self._closing = True
            return Action.ADVANCE
        return Action.DELEGATE


## Image Handler
@final
class Image(ContainerInline):
    def __init__(self) -> None:
        self._bang_consumed: bool = False
        self._opened: bool = False
        self._closing: bool = False
        self._url_open: bool = False
        self._url: str = ""

    @property
    def url(self) -> str:
        return self._url

    @classmethod
    def matches(cls, current: str, peek: str, /) -> Self | None:
        if current == "!" and peek == "[":
            return cls()

        return None

    def __call__(self, current: str, peek: str, /) -> Action:
        if not self._bang_consumed:
            self._bang_consumed = True
            return Action.ADVANCE
        if not self._opened:
            self._opened = True
            return Action.ADVANCE
        if self._closing:
            if not self._url_open:
                if current == "(":
                    self._url_open = True
                    return Action.ADVANCE
                return Action.POP
            if current == ")":
                return Action.POP_AND_ADVANCE
            self._url += current
            return Action.ADVANCE
        if current == "]":
            self._closing = True
            return Action.ADVANCE
        return Action.DELEGATE


## Strikethrough Handler
@final
class Strikethrough(ContainerInline):
    def __init__(self) -> None:
        self._opener_count: int = 0
        self._closer_started: bool = False

    @classmethod
    def matches(cls, current: str, peek: str, /) -> Self | None:
        if current == "~" and peek == "~":
            return cls()

        return None

    def __call__(self, current: str, peek: str, /) -> Action:
        if self._opener_count < 2:
            self._opener_count += 1
            return Action.ADVANCE
        if current == "~":
            if self._closer_started:
                return Action.POP_AND_ADVANCE
            self._closer_started = True
            return Action.ADVANCE
        self._closer_started = False
        return Action.DELEGATE
