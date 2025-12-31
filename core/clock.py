class Clock:
    def __init__(self) -> None:
        self._time: int = 0

    @property
    def now(self) -> int:
        return self._time

    @now.setter
    def now(self) -> None:
        raise AttributeError("time is read only")

    @now.deleter
    def now(self) -> None:
        raise AttributeError("time cannot be deleted")

    def advance_to(self, timestamp: int) -> None:
        if timestamp < self._time:
            raise ValueError("TIme cannot move backwards")
        self._time = timestamp