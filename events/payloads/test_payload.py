from dataclasses import dataclass

from common.types import OrderId


@dataclass(frozen=True, slots=True)
class TestingPayload:
    order_id: OrderId