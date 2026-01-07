#STL
from collections.abc import MutableMapping

from events.payloads import OrderPayload, OrderFillPayload
from common.types import OrderId



class PositionManager:
    def __init__(self, cash: float = 0.0) -> None:
        self._orders: MutableMapping[OrderId, OrderPayload] = {}
        self._cash: float = cash

    def add_order(self, order: OrderPayload) -> None:
        self._orders[order.order_id] = order

    def on_fill(self, fill: OrderFillPayload) -> None:
        pass
