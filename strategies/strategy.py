# STL
from abc import ABC, abstractmethod


# Custom
from events.event import Event
from common.types import StrategyID
from .signal import Signal




class Strategy(ABC):
    @property
    @abstractmethod
    def strategy_id(self) -> StrategyID: ...

    @abstractmethod
    def on_event(self, event: Event) -> Signal: ...
