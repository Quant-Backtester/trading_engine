# STL
from dataclasses import dataclass

# custom
from .payloads import (
    EventPayload,
    MarketDataPayload,
    MarketDataTestPayload,
    OrderFillPayload,
    TimerPayload,
)

from common.types import Timestamp
from common.enums import EventEnum


_EVENT_PAYLOAD_MAP = {
    EventEnum.MARKET_DATA: (
        MarketDataPayload,
        MarketDataTestPayload,
    ),
    EventEnum.ORDER_FILL: (OrderFillPayload,),
    EventEnum.TIMER: (TimerPayload,),
}


@dataclass(frozen=True, slots=True)
class Event:
    timestamp: Timestamp
    event_type: EventEnum
    payload: EventPayload

    def __post_init__(self) -> None:
        allowed_types = _EVENT_PAYLOAD_MAP.get(self.event_type)
        if allowed_types is None:
            raise ValueError(f"Unknown event type: {self.event_type}")

        if not isinstance(self.payload, allowed_types):
            expected_types = ", ".join(t.__name__ for t in allowed_types)
            actual_type = type(self.payload).__name__
            raise TypeError(
                f"Invalid payload type for {self.event_type}: "
                f"expected one of [{expected_types}], got {actual_type}"
            )
