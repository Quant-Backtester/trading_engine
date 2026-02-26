from .signal import Signal, NullSignal
from .strategy import Strategy
from events.event import Event
from .strategy_enum import StrategyEnum


class DummyStrategy(Strategy):
    def __init__(self):
        self.events: list[Event] = []

    @property
    def strategy_id(self) -> StrategyEnum:
        return StrategyEnum.DUMMY

    def on_event(self, event: Event) -> Signal:
        self.events.append(event)
        return NullSignal()
