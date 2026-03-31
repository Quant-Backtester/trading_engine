# STL
from dataclasses import dataclass

# custom
from .payloads import (
    MarketDataPayload,
    OrderFillPayload,
    TimerPayload,
)

from common.types import Timestamp
from common.mixins import ReprMixin


@dataclass(frozen=True, slots=True)
class MarketDataEvent(ReprMixin):
    timestamp: Timestamp
    payload: MarketDataPayload


@dataclass(frozen=True, slots=True)
class OrderFillEvent(ReprMixin):
    timestamp: Timestamp
    payload: OrderFillPayload


@dataclass(frozen=True, slots=True)
class TimerEvent(ReprMixin):
    timestamp: Timestamp
    payload: TimerPayload


type Event = MarketDataEvent | OrderFillEvent | TimerEvent
