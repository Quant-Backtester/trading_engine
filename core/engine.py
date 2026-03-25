# STL
from collections import defaultdict
from collections.abc import (
    MutableSequence,
    MutableMapping,
    Callable,
    MutableSet,
)
import logging

# Custom
from events.event import Event, MarketDataEvent, OrderFillEvent, TimerEvent
from strategies.signal import Signal
from .clock import Clock
from .event_queue import EventQueue
from .portfolio import Portfolio
from .order_manager import OrderManager
from .position_manager import PositionManager
from strategies import Strategy
from common.types import Cash

type Handler = Callable[[Event], None]
type Handlers = MutableSequence[Handler]
type Strategies = MutableMapping[int, Strategy]

logger: logging.Logger = logging.getLogger("engine")


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


class Engine:
    def __init__(self, initial_cash: Cash = 100000) -> None:
        self._initial_cash = initial_cash
        self._setup()
        logger.info("engine setup successfully")

    def _setup(self) -> None:
        self._queue: EventQueue = EventQueue()
        self._clock: Clock = Clock()
        self._strategy_handler = StrategyHandler()
        self._portfolio = Portfolio(initial_capital=self._initial_cash)
        self._orderManager = OrderManager()
        self._positionManager = PositionManager(initial_cash=self._initial_cash)

    def reset(self) -> None:
        self._setup()
        logger.info("reset sucessfully")

    def push_event(self, event: Event) -> None:
        self._queue.push(event=event)

    def run(self) -> None:
        logger.info("engine started running")
        while len(self._queue) > 0:
            event = self._queue.pop()
            self._clock.advance_to(timestamp=event.timestamp)

            logger.debug(
                "Dispatching event: type=%s ts=%d",
                event.timestamp,
            )

            if orders := self._orderManager.on_event(event=event):
                self._positionManager.on_fill_sequence(fills=orders)

            for signal in self._strategy_handler.run_all_strategy(event=event):
                self._orderManager.handle_signal(
                    signal=signal, time=self._clock.now
                )

        logger.info("engine stopped running")
