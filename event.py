from dataclasses import dataclass

# custom
from common.enums import EventEnum
from common.payloads import Eventpayload
from common.types import Timestamp


@dataclass(frozen=True, slots=True)
class Event[T: Eventpayload]:
    timestamp: Timestamp
    event_type: EventEnum
    payload: T
