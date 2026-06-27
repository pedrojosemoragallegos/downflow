from __future__ import annotations

from typing import Self, final

from downflow.action import Action

from .base import Handler


## INLINE-CONTAINER HANDLER
class ContainerInline(Handler): ...


## Emphasis Handler
@final
class Emphasis(ContainerInline):
    @classmethod
    def matches(cls, current: str, peek: str, /) -> Self | None:
        if current.startswith("*"):
            return cls()

        return None

    def __call__(self, current: str, peek: str, /) -> Action:
        return Action.ADVANCE


## Strong Emphasis Handler
@final
class StrongEmphasis(ContainerInline):
    @classmethod
    def matches(cls, current: str, peek: str, /) -> Self | None:
        if current.startswith("**"):
            return cls()

        return None

    def __call__(self, current: str, peek: str, /) -> Action:
        return Action.ADVANCE


## Link Handler
@final
class Link(ContainerInline):
    @classmethod
    def matches(cls, current: str, peek: str, /) -> Self | None:
        if current.startswith("["):
            return cls()

        return None

    def __call__(self, current: str, peek: str, /) -> Action:
        return Action.ADVANCE


## Image Handler
@final
class Image(ContainerInline):
    @classmethod
    def matches(cls, current: str, peek: str, /) -> Self | None:
        if current.startswith("!["):
            return cls()

        return None

    def __call__(self, current: str, peek: str, /) -> Action:
        return Action.ADVANCE
