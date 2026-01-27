from collections.abc import MutableMapping
import logging

from events.payloads import OrderPayload
from common.types import OrderId


type OrderMapping = MutableMapping[OrderId, OrderPayload]


logger = logging.getLogger("engine")


class OrderManager:
    __slots__ = ("_orders",)

    def __init__(self) -> None:
        self._orders: OrderMapping = {}

    def cancel_order(self, order_id: OrderId) -> None:
        self._orders.pop(order_id)

    def add_order(self, order: OrderPayload) -> None:
        if self._orders[order.order_id]:
            logger.info("order %s already exist.", order.order_id)
            return
        self._orders[order.order_id] = order
        logger.info("order with OrderID: %s is setted", order.order_id)
