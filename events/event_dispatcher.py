from collections import defaultdict
from collections.abc import Callable
from .event import Event


class EventDispatcher:
    def __init__(self) -> None:
        self._handlers: defaultdict[type, list[Callable[..., object]]] = (
            defaultdict(list)
        )

    def register(self, event_type: type, callback: Callable) -> None:
        self._handlers[event_type].append(callback)

    def dispatch(self, event: Event) -> None:
        for handler in self._handlers.get(type(event), []):
            handler(event)
