# STL
from abc import ABC, abstractmethod


# Custom
from events.event import Event
from common.types import StrategyID
from events.payloads import OrderPayload




class Strategy(ABC):
    @property
    def strategy_id(self) -> StrategyID: ...

    @abstractmethod
    def on_event(self, event: Event) -> OrderPayload: ...
