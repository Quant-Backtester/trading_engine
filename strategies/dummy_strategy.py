from .strategy import Strategy
from events.event import Event
from common.types import StrategyID
from .strategy_enum import StrategyEnum


class DummyStrategy(Strategy):
    def __init__(self):
        self.events: list[Event] = []

    @property
    def strategy_id(self) -> StrategyID:
        return StrategyEnum.DUMMY

    def on_event(self, event: Event) -> None:
        self.events.append(event)

    def on_order_fill(self, event: Event) -> None:
        return super().on_order_fill(event)
