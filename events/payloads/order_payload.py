# STL
from dataclasses import dataclass

# Custom
from common.enums import Side, OrderType
from common.types import OrderId, Symbol, Quantity, Price, Timestamp


@dataclass(frozen=True, slots=True)
class OrderPayload:
    timestamp: Timestamp
    order_id: OrderId
    symbol: Symbol
    side: Side
    quantity: Quantity
    order_type: OrderType
    price: Price


@dataclass(frozen=True, slots=True)
class OrderFillPayload:
    order: OrderPayload
    fill_timestamp: Timestamp
    fill_price: Price
    fill_quantity: Quantity
    remaining_quantity: Quantity
