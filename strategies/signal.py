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
    take_profit: Price | None = None
    stop_loss: Price | None = None


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
    """Request to close an existing position.

    Fields
    ------
    order_id : specific fill to close. When None, the engine closes across
        the symbol's position group using `quantity`/`fraction` (FIFO).
    quantity : absolute share count to close. Ignored if `order_id` is set.
    fraction : fraction of the current symbol group to close (0.0–1.0).
        Ignored if `order_id` or `quantity` is set. When all three are None,
        the engine closes the entire open position for the symbol.
    """
    order_id: OrderId
    quantity: Quantity | None = None
    fraction: float | None = None
    reason: str | None = None
