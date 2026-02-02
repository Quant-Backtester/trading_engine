from .market_payload import MarketDataPayload, MarketDataTestPayload, MarketData as MarketData
from .test_payload import TestingPayload
from .timer_payload import TimerPayload
from .order_payload import (
    OrderFillPayload,
    OrderPayload,
)

type EventPayload = (
    MarketDataPayload
    | OrderFillPayload
    | TimerPayload
    | TestingPayload
    | OrderPayload
    | MarketDataTestPayload
)
