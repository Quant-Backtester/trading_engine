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

