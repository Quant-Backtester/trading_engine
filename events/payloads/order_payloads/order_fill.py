from dataclasses import dataclass

from common.types import OrderId, Price, Quantity


@dataclass(frozen=True, slots=True)
class OrderFillPayload:
    order_id: OrderId
    fill_price: Price
    fill_quantity: Quantity