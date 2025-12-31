# STL
from dataclasses import dataclass

# Custom
from events.enums import EventEnum
from events.payloads import MarketDataPayload
from sources import MarketDataRSource
from core.engine import Engine
from events.event import Event


class MarketPlayerReplayer:
    def __init__(self, source: MarketDataRSource) -> None:
        self._source: MarketDataRSource = source

    def replay(self, engine: Engine) -> None:
        last_ts: int | None = None

        for record in self._source:
            self.pass_market_data(
                record=record, last_ts=last_ts, engine=engine
            )
            last_ts = record.timestamp

    def pass_market_data(
        self, record: MarketDataPayload, last_ts: int | None, engine: Engine
    ) -> None:
        self._validate_ordering(current_ts=record.timestamp, last_ts=last_ts)

        payload = MarketDataPayload(
            symbol=record.symbol,
            price=record.price,
            volume=record.volume,
            timestamp=record.timestamp,
        )

        event = Event(
            timestamp=record.timestamp,
            event_type=EventEnum.MARKET_DATA,
            payload=payload,
        )

        engine.push_event(event)


    @staticmethod
    def _validate_ordering(
        current_ts: int, last_ts: int | None
    ) -> None:
        if last_ts is not None and current_ts < last_ts:
            raise ValueError("Market data out of order")