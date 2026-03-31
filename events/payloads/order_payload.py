# STL
from abc import ABC
from dataclasses import dataclass
from typing import Any, Self

# Custom
from common.enums import Side, OrderType
from common.mixins import ReprMixin
from common.types import OrderId, Symbol, Quantity, Price, Timestamp


@dataclass(frozen=True, slots=True)
class GenericOrder(ABC, ReprMixin):
    timestamp: Timestamp
    order_id: OrderId
    symbol: Symbol
    side: Side
    price: Price
    quantity: Quantity
    take_profit: Price | None = None
    stop_loss: Price | None = None


@dataclass(frozen=True, slots=True)
class MarketOrderPayload(GenericOrder):
    pass


@dataclass(frozen=True, slots=True)
class LimitOrderPayload(GenericOrder):
    pass


@dataclass(frozen=True, slots=True)
class OrderPayload(ReprMixin):
    timestamp: Timestamp
    order_id: OrderId
    symbol: Symbol
    side: Side
    quantity: Quantity
    order_type: OrderType
    price: Price
    take_profit: Price | None = None
    stop_loss: Price | None = None


@dataclass(frozen=True, slots=True)
class OrderFillPayload(ReprMixin):
    order: OrderPayload
    fill_timestamp: Timestamp
    fill_price: Price
    fill_quantity: Quantity
    remaining_quantity: Quantity
