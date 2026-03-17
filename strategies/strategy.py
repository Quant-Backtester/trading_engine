# STL
from abc import ABC, abstractmethod


# Custom
from events.event import Event
from .strategy_enum import StrategyEnum
from .signal import Signal


class Strategy(ABC):
    @property
    @abstractmethod
    def strategy_id(self) -> StrategyEnum: ...

    @abstractmethod
    def on_event(self, event: Event) -> Signal: ...
