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

    def advance(self, count: int = 1) -> None:
        self._position: int = min(self._position + count, len(self._text))
