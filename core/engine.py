# STL
from collections import defaultdict
from collections.abc import MutableSequence, MutableMapping, Callable
import logging

# Custom
import events.event as event
from events.enums import EventEnum
from .clock import Clock
from .event_queue import EventQueue
from strategies import Strategy

type Handler = Callable[[event.Event], None]
type Handlers = MutableSequence[Handler]
type Dispatcher = MutableMapping[EventEnum, list[Handler]]
type Strategies = MutableSequence[Strategy]


logger = logging.getLogger("engine")


class Engine:
    def __init__(self) -> None:
        self._queue: EventQueue = EventQueue()
        self._clock: Clock = Clock()
        self._running: bool = False
        self._handlers: Dispatcher = defaultdict(list)
        self._strategies: Strategies = []
        logger.info("engine setup successfully")

    def push_event(self, event: event.Event) -> None:
        self._queue.push(event=event)

    def register_handler(self, event_type: EventEnum, handler: Handler) -> None:
        self._handlers[event_type].append(handler)

    def register_strategy(self, strategy: Strategy) -> None:
        self._strategies.append(strategy)

    def get_handlers(self, event: EventEnum) -> list[Handler]:
        return self._handlers.get(event, [])

    def run(self) -> None:
        self._running = True
        while self._running and len(self._queue) > 0:
            event = self._queue.pop()
            self._clock.advance_to(timestamp=event.timestamp)
            self._dispatch(event=event)

            logger.debug(
                "Dispatching event: type=%s ts=%d",
                event.event_type.name,
                event.timestamp,
            )

            for strategy in self._strategies:
                strategy.on_event(event)

        self.stop()
        logger.debug("engine stopped")

    def stop(self) -> None:
        self._running = False

    def _dispatch(self, event: event.Event) -> None:
        handlers: Handlers = self.get_handlers(event=event.event_type)

        for handler in handlers:
            handler(event)
