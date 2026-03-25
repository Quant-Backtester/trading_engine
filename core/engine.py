# STL
from collections import defaultdict
from collections.abc import MutableSequence, MutableMapping, Callable
import logging

# Custom
from events.event import Event
from strategies.signal import Signal
from .clock import Clock
from .event_queue import EventQueue
from .portfolio import Portfolio
from .order_manager import OrderManager
from .position_manager import PositionManager
from strategies import Strategy
from strategies.strategy_enum import StrategyEnum
from common.types import Cash

type Handler = Callable[[Event], None]
type Handlers = MutableSequence[Handler]
type Strategies = MutableMapping[StrategyEnum, list[Strategy]]


logger: logging.Logger = logging.getLogger("engine")


class Engine:
    def __init__(self, initial_cash: Cash = 100000) -> None:
        self._initial_cash = initial_cash
        self._setup()
        logger.info("engine setup successfully")

    def _setup(self) -> None:
        self._queue: EventQueue = EventQueue()
        self._clock: Clock = Clock()
        self._strategies: Strategies = defaultdict(list)
        self._portfolio = Portfolio(initial_capital=self._initial_cash)
        self._orderManager = OrderManager()
        self._positionManager = PositionManager(initial_cash=self._initial_cash)

    def reset(self) -> None:
        self._setup()
        logger.info("reset sucessfully")

    def push_event(self, event: Event) -> None:
        self._queue.push(event=event)

    def register_strategy(self, strategy: Strategy) -> None:
        self._strategies[strategy.strategy_id].append(strategy)

    def unregister_strategy(self, strategy_id: StrategyEnum) -> None:
        self._strategies.pop(strategy_id)

    def start(self) -> None:
        self._running = True
        logger.info("engine started running")

    def run(self) -> None:
        self.start()
        while self._running and len(self._queue) > 0:
            event = self._queue.pop()
            self._clock.advance_to(timestamp=event.timestamp)

            logger.debug(
                "Dispatching event: type=%s ts=%d",
                event.timestamp,
            )

            orders = self._orderManager.on_event(event=event)

            for strategy_id, strategies in self._strategies.items():
                for strategy in strategies:
                    logger.info("on event %s", strategy_id)
                    signal: Signal = strategy.on_event(event=event)
                    self._orderManager.handle_signal(
                        signal=signal, time=self._clock.now
                    )

            self._positionManager.on_fill_sequence(orders)

        self.stop()

    def update_portfolio(self) -> None:
        pass

    def stop(self) -> None:
        self._running = False
        logger.info("engine stopped running")
