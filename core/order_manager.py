from collections.abc import MutableMapping, Sequence
import logging

from events.payloads import OrderPayload, OrderFillPayload
from common.types import OrderId
from events.event import Event
from common.enums import EventEnum, Side
from events.payloads import MarketDataPayload


type OrderMapping = MutableMapping[OrderId, OrderPayload]


logger = logging.getLogger("engine")


class OrderManager:
    __slots__ = ("_orders",)

    def __init__(self) -> None:
        self._orders: OrderMapping = {}

    def remove_order(self, order_id: OrderId) -> None:
        self._orders.pop(order_id)

    def add_order(self, order: OrderPayload) -> None:
        if self._orders[order.order_id]:
            logger.info("order %s already exist.", order.order_id)
            return
        self._orders[order.order_id] = order
        logger.info("order with OrderID: %s is setted", order.order_id)

    def handle_market_data(
        self, data: MarketDataPayload
    ) -> Sequence[OrderFillPayload | None]:
        """simplfied. no orderbook and partial fill at the moment"""

        def get_order_fill(
            order: OrderPayload, data: MarketDataPayload
        ) -> OrderFillPayload:
            return OrderFillPayload(
                order=order,
                fill_price=data.price,
                fill_quantity=order.quantity,
                remaining_quantity=0,
                fill_timestamp=data.timestamp,
            )

        filled_order: Sequence = []
        price = data.price
        for order in self._orders.values():
            if (order.side == Side.BUY and order.price >= price) or (
                order.side == Side.SELL and order.price <= price
            ):
                filled_order.append(get_order_fill(order=order, data=data))
                self.remove_order(order.order_id)

        return filled_order

    def on_event(self, event: Event) -> Sequence[OrderFillPayload | None]:
        if event.event_type == EventEnum.MARKET_DATA:
            return self.handle_market_data(data=event.payload) # type: ignore
        return []
