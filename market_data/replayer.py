# STL

# external


# Custom
from .sources import MarketDataSource
from events.enums import EventEnum
from events.payloads import MarketDataPayload
from core.engine import Engine
from events.event import Event


class MarketDataReplayer:
    def __init__(self, source: MarketDataSource) -> None:
        self._source: MarketDataSource = source

    def replay(self, engine: Engine) -> None:
        last_ts: int | None = None

        for record in self._source:
            self._emit_market_event(
                record=record, last_ts=last_ts, engine=engine
            )
            last_ts = record.timestamp

    def _emit_market_event(
        self,
        record: MarketDataPayload,
        last_ts: int | None,
        engine: Engine,
    ) -> None:
        self._validate_ordering(current_ts=record.timestamp, last_ts=last_ts)

        event = Event(
            timestamp=record.timestamp,
            event_type=EventEnum.MARKET_DATA,
            payload=record,
        )

        engine.push_event(event)

    @staticmethod
    def _validate_ordering(current_ts: int, last_ts: int | None) -> None:
        if last_ts is not None and current_ts < last_ts:
            raise ValueError("Market data out of order")
