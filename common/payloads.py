from dataclasses import dataclass

# Custom
from .types import Symbol, Price, OrderId, Quantity, Volume, TimerId
from .enums import Side, TimerEnum


@dataclass(frozen=True, slots=True)
class MarketDataPayload:
    symbol: Symbol
    price: Price
    volume: Volume


@dataclass(frozen=True, slots=True)
class OrderFillPayload:
    order_id: OrderId
    fill_price: Price
    quantity: Quantity


@dataclass(frozen=True, slots=True)
class OrderSubmitPayload:
    order_id: OrderId
    symbol: Symbol
    side: Side
    quantity: Quantity
    price: Price


@dataclass(frozen=True, slots=True)
class OrderCancelPayload:
    order_id: OrderId


@dataclass(frozen=True, slots=True)
class TimerPayload:
    kind: TimerEnum
    timer_id: TimerId
    target: str | None = None
    interval_ns: int | None = None
    metadata: dict[str, str] | None = None

@dataclass(frozen=True, slots=True)
class TestingPayload:
    order_id: OrderId


type Eventpayload = (
    MarketDataPayload
    | OrderFillPayload
    | OrderSubmitPayload
    | TimerPayload
    | OrderCancelPayload
    | TestingPayload
)