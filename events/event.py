# STL
from dataclasses import dataclass

# custom
from .payloads import Eventpayload

from common.types import Timestamp
from .enums import EventEnum


@dataclass(frozen=True, slots=True)
class Event:
    timestamp: Timestamp
    event_type: EventEnum
    payload: Eventpayload
