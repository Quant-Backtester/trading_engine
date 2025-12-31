from .market_data import MarketDataPayload
from .order_cancel import OrderCancelPayload
from .order_fill import OrderFillPayload
from .order_submit import OrderSubmitPayload
from .test import TestingPayload
from .timer import TimerPayload

type Eventpayload = (
    MarketDataPayload
    | OrderFillPayload
    | OrderSubmitPayload
    | TimerPayload
    | OrderCancelPayload
    | TestingPayload
)
