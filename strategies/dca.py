from events.event import Event
from events.payloads.market_payload import MarketDataPayload
from strategies.signal import AddSignal, NullSignal, Signal
from common.enums import OrderType, Side

from .strategy import Strategy
from common.types import Quantity


class DCA(Strategy):
    __slots__ = "_buyframe", "_buy_amount", "_last_buy_time"

    def __init__(self, buyframe: int, buy_amount: Quantity) -> None:
        self._buyframe: int = buyframe
        self._buy_amount: Quantity = buy_amount
        self._last_buy_time: int | None = None

    def get_hash_key(self) -> tuple[object, ...]:
        return (self._buy_amount, self._buyframe)

    def on_event(self, event: Event) -> Signal:
        currnet_time = event.timestamp

        if isinstance(event.payload, MarketDataPayload) and self._should_buy(
            current_timestamp=currnet_time
        ):
            self._last_buy_time = currnet_time
            return AddSignal(
                side=Side.BUY,
                type=OrderType.MARKET,
                price=event.payload.price,
                symbol=event.payload.symbol,
                quantity=self._buy_amount,
                take_profit=event.payload.price + 20,
                stop_loss=max(0.0, event.payload.price - 10),
            )

        return NullSignal()

    def _should_buy(self, current_timestamp: int) -> bool:
        if self._last_buy_time is None:
            return True

        time_since_last_buy: int = current_timestamp - self._last_buy_time
        return time_since_last_buy > self._buyframe

    def get_next_buy_time(self) -> int | None:
        if self._last_buy_time is None:
            return None
        return self._last_buy_time + self._buyframe

    def reset(self) -> None:
        self._last_buy_time = None
