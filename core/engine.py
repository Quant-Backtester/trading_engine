# STL
from collections import defaultdict
from collections.abc import MutableSequence, MutableMapping, Callable
import logging

# Custom
from events.event import Event
from common.enums import EventEnum
from .clock import Clock
from .event_queue import EventQueue
from .portfolio import Portfolio
from .order_manager import OrderManager
from strategies import Strategy
from common.types import StrategyID, Cash


type Handler = Callable[[Event], None]
type Handlers = MutableSequence[Handler]
type Dispatcher = MutableMapping[EventEnum, Handlers]
type Strategies = MutableMapping[StrategyID, Strategy]


logger: logging.Logger = logging.getLogger("engine")


class Engine:
    def __init__(self, initial_cash: Cash = 100000) -> None:
        self._initial_cash = initial_cash
        self._setup(initial_cash)
        logger.info("engine setup successfully")

    def _setup(self, initial_cash: Cash) -> None:
        self._queue: EventQueue = EventQueue()
        self._clock: Clock = Clock()
        self._handlers: Dispatcher = defaultdict(list)
        self._strategies: Strategies = {}
        self._portfolio = Portfolio(initial_cash=initial_cash)
        self._orderManager = OrderManager()

    def reset(self) -> None:
        self._setup(initial_cash=self._initial_cash)
        logger.info("reset sucessfully")

    def push_event(self, event: Event) -> None:
        self._queue.push(event=event)

    def register_handler(self, event_type: EventEnum, handler: Handler) -> None:
        self._handlers[event_type].append(handler)

    def unregister_handler(self, event_type: EventEnum) -> None:
        self._handlers.pop(event_type)

    def register_strategy(self, strategy: Strategy) -> None:
        self._strategies[strategy.strategy_id] = strategy

    def unregister_strategy(self, strategy_id: StrategyID) -> None:
        self._strategies.pop(strategy_id)

    def get_handlers(self, event: EventEnum) -> Handlers:
        return self._handlers.get(event, [])

    def start(self) -> None:
        self._running = True
        logger.info("engine started running")

    def run(self) -> None:
        self.start()
        while self._running and len(self._queue) > 0:
            event = self._queue.pop()
            self._clock.advance_to(timestamp=event.timestamp)
            # self._dispatch(event=event)

            logger.debug(
                "Dispatching event: type=%s ts=%d",
                event.event_type.name,
                event.timestamp,
            )

            for strategy_id, strategy in self._strategies.items():
                logger.info("on event %s", strategy_id)
                strategy.on_event(event=event)

        self.stop()

    def update_portfolio(self) -> None:
        pass

    def stop(self) -> None:
        self._running = False
        logger.info("engine stopped running")

    def _dispatch(self, event: Event) -> None:
        handlers: Handlers = self.get_handlers(event=event.event_type)

        for handler in handlers:
            handler(event)
