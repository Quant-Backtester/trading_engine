from collections import defaultdict
from collections.abc import MutableMapping

from events.event import Event
from strategies.signal import Signal
from strategies.strategy import Strategy


type Strategies = MutableMapping[int, Strategy]


class StrategyHandler:
    __slots__ = ("_strategies",)

    def __init__(self) -> None:
        self._strategies: Strategies = defaultdict(Strategy)

    def add_strategy(self, strategy: Strategy) -> bool:
        key = hash(strategy)
        if key in self._strategies:
            return False
        self._strategies[key] = strategy
        return True

    def remove_strategy(self, key: int) -> bool:
        if key not in self._strategies:
            return False
        self._strategies.pop(key)
        return True

    def run_all_strategy(self, event: Event) -> list[Signal]:
        return [
            signal
            for strategy in self._strategies.values()
            if (signal := strategy.on_event(event=event)) is not None
        ]
