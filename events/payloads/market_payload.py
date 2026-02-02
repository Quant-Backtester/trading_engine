from dataclasses import dataclass
from typing import Protocol

from common.types import Price, Symbol, Timestamp, Volume


class MarketData(Protocol):
    timestamp: Timestamp
    symbol: Symbol


# technically this is the one for a more rigorous backtesting engine as OJLC shouldn't be known ahead of time
# the marketdata event format should just have time, price , symbol and other things like volume, volitity etc.
@dataclass(frozen=True, slots=True)
class MarketDataPayload:
    timestamp: Timestamp
    symbol: Symbol
    price: Price
    volume: Volume


@dataclass(frozen=True, slots=True)
class MarketDataTestPayload:
    timestamp: Timestamp
    symbol: Symbol
    open: Price
    high: Price
    low: Price
    close: Price
    volume: Volume
