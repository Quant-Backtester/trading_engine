#STL
from dataclasses import dataclass

#Custom
from events.enums import Side
from common.types import OrderId, Symbol, Quantity


@dataclass(frozen=True, slots=True)
class OrderPayload:
    order_id: OrderId
    symbol: Symbol
    side: Side
    quantity: Quantity
