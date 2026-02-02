from enum import StrEnum, auto, unique


@unique
class EventEnum(StrEnum):
    MARKET_DATA = auto()
    ORDER_SUBMIT = auto()
    ORDER_FILL = auto()
    ORDER_CANCEL = auto()
    TIMER = auto()


@unique
class Side(StrEnum):
    BUY = auto()
    SELL = auto()


@unique
class TimerEnum(StrEnum):
    HEARTBEAT = auto()
    STRATEGY_TICK = auto()
    RISK_CHECK = auto()
    END_OF_DAY = auto()
    BAR_CLOSE = auto()
    SESSION_EVENT = auto()
    CLEANUP = auto()


@unique
class OrderType(StrEnum):
    LIMIT = auto()
    MARKET = auto()

    # implement later
    GTC = auto()
    FOK = auto()
    AON = auto()
    IOC = auto()
    DAY = auto()
