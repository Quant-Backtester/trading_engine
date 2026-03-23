# STL
from dataclasses import dataclass

# custom
from .payloads import (
    MarketDataPayload,
    OrderFillPayload,
    TimerPayload,
)

from common.types import Timestamp


@dataclass(frozen=True, slots=True)
class MarketDataEvent:
    timestamp: Timestamp
    payload: MarketDataPayload


@dataclass(frozen=True, slots=True)
class OrderFillEvent:
    timestamp: Timestamp
    payload: OrderFillPayload


@dataclass(frozen=True, slots=True)
class TimerEvent:
    timestamp: Timestamp
    payload: TimerPayload


type Event = MarketDataEvent | OrderFillEvent | TimerEvent
