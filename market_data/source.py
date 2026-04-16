# STL
from os import PathLike
from pathlib import Path
from typing import Protocol, TextIO, runtime_checkable
from collections.abc import Iterator, Iterable, Sequence
import csv
from datetime import datetime

# Custom
from common.mixins import ReprMixin
from events.payloads import MarketDataPayload


@runtime_checkable
class MarketDataSource[T: MarketDataPayload](Protocol):
    __slots__ = ()

    def __iter__(self) -> Iterator[T]: ...


class FakeMarketDataSource(ReprMixin, MarketDataSource):
    __slots__ = ("_records",)

    def __init__(self, records):
        self._records: Iterable = records

    def __iter__(self):
        return iter(self._records)


class CSVMarketDataSource(ReprMixin, MarketDataSource):
    __slots__ = "_path", "_symbol"
    column_mappings = {
        "price": ["price", "Price", "close", "Close"],
        "volume": ["volume", "Volume", "vol", "Vol"],
        "timestamp": ["date", "Date", "timestamp", "Timestamp", "time", "Time"],
    }

    def __init__(self, path: str | PathLike[str]) -> None:
        self._path = Path(path)
        self._symbol = self._path.stem

    def __iter__(self) -> Iterator[MarketDataPayload]:
        with self._path.open("r", newline="") as file:
            yield from self._read_csv_file(file=file)

    def _find_column(
        self,
        available_columns: Sequence[str] | None,
        possible_names: Sequence[str],
    ) -> str | None:
        if available_columns is None:
            return None
        available_set = set(col.lower() for col in available_columns)
        for possible_name in possible_names:
            if possible_name.lower() not in available_set:
                continue
            for col in available_columns:
                if col.lower() == possible_name.lower():
                    return col
        return None

    def _read_csv_file(self, file: TextIO) -> Iterator[MarketDataPayload]:
        reader = csv.DictReader(f=file)

        actual_columns = {}
        for payload_field, possible_names in self.column_mappings.items():
            found_col = self._find_column(reader.fieldnames, possible_names)
            if found_col is None:
                raise ValueError(
                    f"Could not find column for {payload_field}. "
                    f"Available: {reader.fieldnames}"
                )
            actual_columns[payload_field] = found_col

        for row in reader:
            yield MarketDataPayload(
                symbol=self._symbol,
                price=float(row[actual_columns["price"]]),
                volume=int(row[actual_columns["volume"]]),
                timestamp=self.convert_timestamp(
                    timestamp=row[actual_columns["timestamp"]]
                ),
            )

    @staticmethod
    def convert_timestamp(timestamp: str) -> int:
        dt = datetime.strptime(timestamp, "%Y-%m-%d")

        date_int = int(dt.strftime("%Y%m%d"))
        return date_int


class DBMarketDataSource(ReprMixin, MarketDataSource):
    __slots__ = ()
    pass


class JsonMarketDataSource(ReprMixin, MarketDataSource):
    __slots__ = ()
    pass
