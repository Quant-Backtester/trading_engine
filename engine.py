# STL
from collections import defaultdict
from typing import Callable

# Custom
import event
from common.enums import EventEnum

from .clock import Clock
from .event_queue import EventQueue

type Handler = Callable[[event.Event], None]

class Engine:
    def __init__(self) -> None:
        self._queue = EventQueue()
        self._clock = Clock()
        self._running = False
        self._handlers: defaultdict[
            EventEnum, list[Handler]
            ] = defaultdict(list)

    def push_event(self, event: event.Event) -> None:
        self._queue.push(event=event)

    def register_handler(
        self, event_type: EventEnum, handler: Callable[[event.Event], None]
    ) -> None:
        self._handlers[event_type].append(handler)

    def get_handlers(self, event: EventEnum) -> list[Handler]:
        return self._handlers.get(event, [])


    def run(self) -> None:
        self._running = True
        while self._running and len(self._queue) > 0:
            event = self._queue.pop()
            self._clock.advance_to(timestamp=event.timestamp)
            self._dispatch(event=event)

    def stop(self) -> None:
        self._running = False

    def _dispatch(self, event: event.Event) -> None:
        handlers =self.get_handlers(event=event.event_type)

        for handler in handlers:
            handler(event)

