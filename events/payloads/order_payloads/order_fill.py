from dataclasses import dataclass

from common.types import Price, Quantity
from .order import OrderPayload


@dataclass(frozen=True, slots=True)
class OrderFillPayload:
    order: OrderPayload
    fill_price: Price
    fill_quantity: Quantity
