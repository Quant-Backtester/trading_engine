# STL
from os import PathLike
from pathlib import Path
from typing import Protocol, TextIO, runtime_checkable
from collections.abc import Iterator, Iterable
import csv
from datetime import datetime

# Custom
from events.payloads import MarketDataPayload, MarketDataTestPayload, MarketData


class SourceReprMixin:
    __slots__ = ()

    def __str__(self) -> str:
        return self.__class__.__name__

    def __repr__(self) -> str:
        return f"<{self.__class__}>"


@runtime_checkable
class MarketDataSource[T: MarketData](Protocol):
    __slots__ = ()

    def __iter__(self) -> Iterator[T]: ...


class FakeMarketDataSource(SourceReprMixin, MarketDataSource):
    __slots__ = ("_records",)

    def __init__(self, records):
        self._records: Iterable = records

    def __iter__(self):
        return iter(self._records)


class CSVMarketDataSource(SourceReprMixin, MarketDataSource):
    __slots__ = "_path", "_symbol"

    def __init__(self, path: str | PathLike[str]) -> None:
        self._path = Path(path)
        self._symbol = self._path.stem

    def __iter__(self) -> Iterator[MarketDataPayload | MarketDataTestPayload]:
        with self._path.open("r", newline="") as file:
            # yield from self._read_csv_file(file=file)
            yield from self._test_read_csv_file(file=file)

    def _read_csv_file(self, file: TextIO) -> Iterator[MarketDataPayload]:
        for row in csv.DictReader(file):
            yield MarketDataPayload(
                symbol=self._symbol,
                price=float(row["price"]),
                volume=int(row["Volume"]),
                timestamp=int(row["timestamp"]),
            )

    def _test_read_csv_file(
        self, file: TextIO
    ) -> Iterator[MarketDataTestPayload]:
        for row in csv.DictReader(file):
            yield MarketDataTestPayload(
                symbol=self._symbol,
                open=float(row["Open"]),
                high=float(row["High"]),
                low=float(row["Low"]),
                close=float(row["Close"]),
                volume=int(row["Volume"]),
                timestamp=self.convert_timestamp(row["Date"]),
            )

    @staticmethod
    def convert_timestamp(timestamp: str) -> int:
        dt = datetime.strptime(timestamp, "%Y-%m-%d")

        # Convert to YYYYMMDD integer
        date_int = int(dt.strftime("%Y%m%d"))
        return date_int


class DBMarketDataSource(SourceReprMixin, MarketDataSource):
    pass


class JsonMarketDataSource(SourceReprMixin, MarketDataPayload):
    pass
