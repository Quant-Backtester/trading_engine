from dataclasses import dataclass

# custom
from common.enums import EventEnum
from common.types import Timestamp
from common.payloads import Eventpayload


@dataclass(frozen=True, slots=True)
class Event[T: Eventpayload]:
    timestamp: Timestamp
    event_type: EventEnum
    payload: T
