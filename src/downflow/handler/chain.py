from __future__ import annotations

from typing import Generic, TypeVar, final

from .base import Handler

H = TypeVar(name="H", bound=Handler)


@final
class HandlerChain(Generic[H]):
    def __init__(self, *handlers: type[H]) -> None:
        self._handlers: list[type[H]] = list(handlers)

    def append(self, handler: type[H], /) -> None:
        self._handlers.append(handler)

    def __call__(self, current: str, peek: str, /) -> H | None:
        for handler_cls in self._handlers:
            if (handler := handler_cls.matches(current, peek)) is not None:
                return handler

        return None
