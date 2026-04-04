from collections.abc import MutableMapping, Sequence
import logging

from events.payloads import OrderPayload, OrderFillPayload
from common.types import OrderId
from events.event import Event, MarketDataEvent
from common.enums import OrderType, Side
from events.payloads import MarketDataPayload
from strategies.signal import AddSignal, Signal


type OrderMapping = MutableMapping[OrderId, OrderPayload]


logger = logging.getLogger("engine")


class OrderManager:
    __slots__ = ("_orders", "order_id")

    def __init__(self) -> None:
        self._orders: OrderMapping = {}
        self.order_id = 1

    def remove_order(self, order_id: OrderId) -> None:
        self._orders.pop(order_id)

    def add_order(self, order: OrderPayload) -> None:
        if self._orders.get(order.order_id):
            logger.info("order %s already exist.", order.order_id)
            return
        self._orders[order.order_id] = order
        logger.info("order with OrderID: %s is setted", order.order_id)

    def on_market_data(
        self, data: MarketDataPayload
    ) -> Sequence[OrderFillPayload]:
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

        filled_order: list[OrderFillPayload] = []
        to_remove: list[OrderId] = []
        price = data.price
        for order in self._orders.values():
            if (
                (order.side == Side.BUY and order.price >= price)
                or (order.side == Side.SELL and order.price <= price)
                or (order.order_type == OrderType.MARKET)
            ):
                filled_order.append(get_order_fill(order=order, data=data))
                to_remove.append(order.order_id)

        for order_id in to_remove:
            self.remove_order(order_id=order_id)

        return filled_order

    def handle_signal(self, signal: Signal, time: int) -> None:
        if isinstance(signal, AddSignal):
            self.add_order(
                order=OrderPayload(
                    timestamp=time,
                    symbol=signal.symbol,
                    side=signal.side,
                    quantity=signal.quantity,
                    order_type=signal.type,
                    order_id=self.order_id,
                    price=signal.price,
                    take_profit=signal.take_profit,
                    stop_loss=signal.stop_loss,
                )
            )
            self.order_id += 1

    def on_event(self, event: Event) -> Sequence[OrderFillPayload]:
        if isinstance(event, MarketDataEvent):
            return self.on_market_data(data=event.payload)
        return []
