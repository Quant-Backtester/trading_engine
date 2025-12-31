from dataclasses import dataclass

from common.types import OrderId


@dataclass(frozen=True, slots=True)
class OrderCancelPayload:
    order_id: OrderId