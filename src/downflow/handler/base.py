from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Self

if TYPE_CHECKING:
    from downflow.action import Action


class Handler(ABC):
    @classmethod
    @abstractmethod
    def matches(cls, current: str, peek: str, /) -> Self | None: ...

    @abstractmethod
    def __call__(self, current: str, peek: str, /) -> Action: ...
