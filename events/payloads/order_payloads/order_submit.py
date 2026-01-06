from dataclasses import dataclass

from .order import OrderPayload


@dataclass(frozen=True, slots=True)
class OrderSubmitPayload:
    order: OrderPayload