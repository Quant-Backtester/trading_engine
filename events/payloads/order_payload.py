# STL
from dataclasses import dataclass

# Custom
from events.enums import Side
from common.types import OrderId, Symbol, Quantity, Price


@dataclass(frozen=True, slots=True)
class OrderPayload:
    order_id: OrderId
    symbol: Symbol
    side: Side
    quantity: Quantity


@dataclass(frozen=True, slots=True)
class OrderFillPayload:
    order: OrderPayload
    fill_price: Price
    fill_quantity: Quantity


@dataclass(frozen=True, slots=True)
class OrderSubmitPayload:
    order: OrderPayload


@dataclass(frozen=True, slots=True)
class OrderCancelPayload:
    order_id: OrderId
