from __future__ import annotations

from enum import Enum, auto


class Action(Enum):
    ADVANCE = auto()
    PUSH = auto()
    POP = auto()
    POP_AND_ADVANCE = auto()
    DELEGATE = auto()
