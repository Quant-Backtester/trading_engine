from .market_payload import MarketDataPayload, MarketDataTestPayload, MarketData
from .test_payload import TestingPayload
from .timer_payload import TimerPayload
from .order_payload import (
    OrderCancelPayload,
    OrderFillPayload,
    OrderPayload,
    OrderSubmitPayload,
)

type Eventpayload = (
    MarketDataPayload
    | OrderFillPayload
    | OrderSubmitPayload
    | TimerPayload
    | OrderCancelPayload
    | TestingPayload
    | OrderPayload
    | MarketData
    | MarketDataTestPayload
)
