# STL
import logging
from dataclasses import dataclass

# external


# Custom
from .sources import MarketDataSource
from events.enums import EventEnum
from events.payloads import MarketDataPayload
from core.engine import Engine
from events.event import Event


logger = logging.getLogger(__name__)


class MarketDataReplayer:
    def __init__(self, chunk_size: int = 10000) -> None:
        self._source: MarketDataSource | None = None
        self._chunk_size: int = chunk_size

    def check_source(self) -> None:
        if not self._source:
            raise ValueError("Source is None")

    def _replay_in_chunk(self, engine: Engine) -> None:
        self.check_source()

        chunk_buffer: list[MarketDataPayload] = []
        last_ts: int | None = None
        chunk_number = 0

        for record in self._source:  # type: ignore
            self._validate_ordering(
                current_ts=record.timestamp, last_ts=last_ts
            )
            last_ts = record.timestamp

            chunk_buffer.append(record)

            if len(chunk_buffer) >= self._chunk_size:
                self._process_chunk(
                    engine=engine, chunk=chunk_buffer, chunk_number=chunk_number
                )
                chunk_buffer = []
                chunk_number += 1

        if chunk_buffer:
            self._process_chunk(
                engine=engine, chunk=chunk_buffer, chunk_number=chunk_number
            )

    def _process_chunk(
        self, engine: Engine, chunk: list[MarketDataPayload], chunk_number: int
    ) -> None:
        """Process a single chunk of market data"""
        logger.info(
            "Processing chunk %d with %d records", chunk_number, len(chunk)
        )

        last_ts: int | None = None

        for record in chunk:
            self._emit_market_event(
                record=record, last_ts=last_ts, engine=engine
            )
            last_ts = record.timestamp

        engine.run()

        logger.info("Chunk %d completed", chunk_number)

    def replay(self, engine: Engine, chunked: bool = True) -> None:
        self.check_source()

        if chunked:
            self._replay_in_chunk(engine=engine)
            return

        last_ts: int | None = None
        for record in self._source:  # type: ignore
            self._emit_market_event(
                record=record, last_ts=last_ts, engine=engine
            )
            last_ts = record.timestamp
        engine.run()

    def set_market_data_source(self, source: MarketDataSource) -> None:
        self._source = source
        logger.info("data source %s is setted", source)

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
