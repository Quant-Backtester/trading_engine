

class Clock:
    def __init__(self) -> None:
        self._time: int = 0

    @property
    def now(self) -> int:
        return self._time

    def advance_to(self, timestamp: int) -> None:
        if timestamp < self._time:
            raise ValueError("TIme cannot move backwards")
        self._time = timestamp