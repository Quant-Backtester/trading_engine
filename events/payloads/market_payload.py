from dataclasses import dataclass

from common.types import Price, Symbol, Timestamp, Volume


# technically this is the one for a more rigorous backtesting engine as OJLC shouldn't be known ahead of time
# the marketdata event format should just have time, price , symbol and other things like volume, volitity etc.
@dataclass(frozen=True, slots=True)
class MarketDataPayload:
    timestamp: Timestamp
    symbol: Symbol
    price: Price
    volume: Volume
    Open: Price | None = None
    High: Price | None = None
    Low: Price | None = None
    Close: Price | None = None
