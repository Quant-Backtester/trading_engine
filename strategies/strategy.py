from abc import ABC, abstractmethod
from events.event import Event


class Strategy(ABC):
    @abstractmethod
    def on_event(self, event: Event) -> None:
        pass


__all__ = (
    "Strategy",
)