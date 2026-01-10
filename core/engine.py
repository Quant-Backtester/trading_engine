# STL
from collections import defaultdict
from collections.abc import MutableSequence, MutableMapping, Callable
import logging

# Custom
import events.event as event
from events.enums import EventEnum
from .clock import Clock
from .event_queue import EventQueue
from .position_manager import PositionManager
from strategies import Strategy
from common.types import StrategyID

type Handler = Callable[[event.Event], None]
type Handlers = MutableSequence[Handler]
type Dispatcher = MutableMapping[EventEnum, Handlers]
type Strategies = MutableMapping[StrategyID, Strategy]


logger: logging.Logger = logging.getLogger("engine")


class Engine:
    def __init__(self) -> None:
        self._setup()
        logger.info("engine setup successfully")

    def _setup(self) -> None:
        self._queue: EventQueue = EventQueue()
        self._clock: Clock = Clock()
        self._handlers: Dispatcher = defaultdict(list)
        self._strategies: Strategies = {}
        self.position_manager: PositionManager = PositionManager()

    def reset(self) -> None:
        self._setup()
        logger.info("reset sucessfully")

    def push_event(self, event: event.Event) -> None:
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
        logger.info("engine started")

    def run(self) -> None:
        self.start()
        while self._running and len(self._queue) > 0:
            event = self._queue.pop()
            self._clock.advance_to(timestamp=event.timestamp)
            self._dispatch(event=event)

            logger.debug(
                "Dispatching event: type=%s ts=%d",
                event.event_type.name,
                event.timestamp,
            )

            for strategy_id, strategy in self._strategies.items():
                logger.info("on event %s", strategy_id)
                strategy.on_event(event=event)

        self.stop()

    def stop(self) -> None:
        self._running = False
        logger.debug("engine stopped")

    def _dispatch(self, event: event.Event) -> None:
        handlers: Handlers = self.get_handlers(event=event.event_type)

        for handler in handlers:
            handler(event)
