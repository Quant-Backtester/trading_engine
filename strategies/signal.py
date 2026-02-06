from dataclasses import dataclass
from enum import StrEnum, auto, unique
from abc import ABC

from common.enums import Side
from common.types import Price, OrderId, Quantity


@unique
class SignalType(StrEnum):
    ADD = auto()
    CANCEL = auto()


class Signal(ABC):
    __slots__ = ()


class NullSignal(Signal):
    __slots__ = ()


@dataclass(slots=True, frozen=True)
class AddSignal(Signal):
    side: Side
    price: Price
    takeProfit: Price | None
    stopLoss: Price | None


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
