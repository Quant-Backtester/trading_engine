from dataclasses import dataclass

from enums import TimerEnum

from common.types import TimerId


@dataclass(frozen=True, slots=True)
class TimerPayload:
    kind: TimerEnum
    timer_id: TimerId
    target: str | None = None
    interval_ns: int | None = None
    metadata: dict[str, str] | None = None
