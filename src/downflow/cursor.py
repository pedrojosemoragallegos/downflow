from __future__ import annotations

from typing import final


@final
class Cursor:
    def __init__(self, text: str, /) -> None:
        self._text: str = text
        self._position: int = 0

    @property
    def current(self) -> str:
        return self._text[self._position]

    @property
    def position(self) -> int:
        return self._position

    @property
    def peek(self) -> str | None:
        if self._position + 1 < len(self._text):
            return self._text[self._position + 1]

        return None

    @property
    def is_exhausted(self) -> bool:
        return self._position >= len(self._text)

    def advance(self) -> None:
        self._position += 1
