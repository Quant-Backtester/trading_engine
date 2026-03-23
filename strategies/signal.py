from dataclasses import dataclass
from enum import StrEnum, auto, unique
from abc import ABC

from common.enums import OrderType, Side
from common.types import Price, OrderId, Quantity, Symbol


class Signal(ABC):
    __slots__ = ()


class NullSignal(Signal):
    __slots__ = ()


@dataclass(slots=True, frozen=True)
class AddSignal(Signal):
    symbol: Symbol
    side: Side
    type: OrderType
    price: Price
    quantity: Quantity
    takeProfit: Price | None = None
    stopLoss: Price | None = None


@dataclass(slots=True, frozen=True)
class CancelSignal(Signal):
    orderId: OrderId


@dataclass(slots=True, frozen=True)
class ModifySignal(Signal):
    order_id: OrderId
    new_price: Price | None = None
    new_quantity: Quantity | None = None
    new_take_profit: Price | None = None
    new_stop_loss: Price | None = None


@dataclass(slots=True, frozen=True)
class CloseSignal(Signal):
    position_id: OrderId
    quantity: Quantity | None = None
    reason: str | None = None
