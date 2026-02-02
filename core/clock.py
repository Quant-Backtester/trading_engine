from common.types import Timestamp


class Clock:
    __slots__ = ("_time",)

    def __init__(self) -> None:
        self._time: Timestamp = 0

    @property
    def now(self) -> Timestamp:
        return self._time

    @now.setter
    def now(self, new_value) -> None:
        raise AttributeError("time is read only")

    @now.deleter
    def now(self) -> None:
        raise AttributeError("time cannot be deleted")

    def advance_to(self, timestamp: Timestamp) -> None:
        if timestamp < self._time:
            raise ValueError("TIme cannot move backwards")
        self._time = timestamp
