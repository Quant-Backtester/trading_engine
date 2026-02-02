from enum import IntEnum, unique, auto


@unique
class StrategyEnum(IntEnum):
    DUMMY = auto()
    DCA = auto()
