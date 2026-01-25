from .market_data import MarketDataPayload, MarketDataTestPayload
from .order_payloads import OrderSubmitPayload, OrderPayload, OrderCancelPayload, OrderFillPayload
from .test import TestingPayload
from .timer import TimerPayload

type Eventpayload = (
    MarketDataPayload
    | OrderFillPayload
    | OrderSubmitPayload
    | TimerPayload
    | OrderCancelPayload
    | TestingPayload
    | OrderPayload
)
