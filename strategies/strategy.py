# STL
from typing import Protocol, runtime_checkable


# Custom
from events.event import Event
from common.types import StrategyID


@runtime_checkable
class Strategy(Protocol):
    @property
    def strategy_id(self) -> StrategyID: ...

    """ Do not define a setter/deleter for strategy id, it should be immutable """

    def on_event(self, event: Event) -> None:
        pass

    def on_order_fill(self, event: Event) -> None:
        pass
