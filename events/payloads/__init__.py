from .market_payload import (
    MarketDataPayload,
    MarketDataTestPayload,
    MarketData as MarketData,
)
from .test_payload import TestingPayload
from .timer_payload import TimerPayload
from .order_payload import (
    OrderFillPayload,
    OrderPayload,
)

type MarketPayloads = MarketDataPayload | MarketDataTestPayload
type OrderPayloas = OrderPayload | OrderFillPayload
type SystemPayloads = TimerPayload | TestingPayload

type EventPayload = MarketPayloads | OrderPayloas | SystemPayloads
