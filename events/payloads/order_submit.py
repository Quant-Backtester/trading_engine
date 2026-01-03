from dataclasses import dataclass

from events.enums import Side

from common.types import OrderId, Price, Quantity, Symbol


@dataclass(frozen=True, slots=True)
class OrderSubmitPayload:
    order_id: OrderId
    symbol: Symbol
    side: Side
    quantity: Quantity
    price: Price