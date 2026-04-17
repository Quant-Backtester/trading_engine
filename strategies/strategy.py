# STL
from abc import ABC, abstractmethod


# Custom
from events.event import Event
from common.mixins import ReprMixin
from .signal import Signal


class Strategy(ABC, ReprMixin):
    @abstractmethod
    def on_event(self, event: Event) -> Signal: ...

    @abstractmethod
    def get_hash_key(self) -> tuple[object, ...]: ...

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Strategy):
            return False
        return self.get_hash_key() == other.get_hash_key()

    def __hash__(self) -> int:
        return hash(self.get_hash_key())
