# STL
from collections import defaultdict
from collections.abc import MutableMapping, Sequence
from dataclasses import dataclass, field

# Custom
from events.payloads import OrderFillPayload, MarketDataPayload
from common.types import Percentage, Price, Symbol, Cash, Quantity
from common.enums import Side


@dataclass(slots=True)
class SymbolPositionGroup:
    price: Price
    positions: list[OrderFillPayload] = field(default_factory=list)

    @property
    def total_quantity(self) -> Quantity:
        return sum(p.fill_quantity for p in self.positions)

    @property
    def avg_price(self) -> Price:
        total_quantity = self.total_quantity
        if total_quantity == 0:
            return 0.0

        return (
            sum(p.fill_quantity * p.fill_price for p in self.positions)
            / total_quantity
        )


class PositionManager:
    __slots__ = ("_positions", "_cash", "_realized_pnl")

    def __init__(self, initial_cash: Cash = 0.0) -> None:
        self._cash: Cash = initial_cash
        self._realized_pnl: Cash = 0.0

    def get_position(self, symbol: Symbol) -> list[Position] | None:
        return self._positions.get(symbol, None)

    def _set_new_position(self, symbol: Symbol) -> Position:
        pos = self.get_position(symbol=symbol)
        pos = Position(symbol=symbol)
        self._positions[symbol].append(pos)
        return pos

    def on_market_data(self, md: MarketDataPayload) -> None:
        pos = self._positions.get(md.symbol)
        if pos is None:
            return

        pos.last_price = md.price

    @property
    def cash(self) -> Cash:
        return self._cash

    @property
    def realized_pnl(self) -> Cash:
        return self._realized_pnl

    @property
    def total_unrealized_pnl(self) -> Cash:
        return sum(pos.unrealized_pnl for pos in self._positions.values())

    @staticmethod
    def _validate_fill(fill: OrderFillPayload) -> None:
        assert fill.fill_quantity > 0
        assert fill.fill_price > 0
        assert isinstance(fill.order.side, Side)

    @staticmethod
    def _signed_quantity(fill: OrderFillPayload) -> Quantity:
        return (
            fill.fill_quantity
            if fill.order.side == Side.BUY
            else -fill.fill_quantity
        )

    @staticmethod
    def _is_open_or_add(pos: Position, signed_qty: Quantity) -> bool:
        return pos.quantity == 0 or pos.quantity * signed_qty > 0

    @staticmethod
    def _apply_open_or_add(
        pos: Position,
        signed_qty: Quantity,
        price: Price,
    ) -> None:
        new_qty = pos.quantity + signed_qty

        pos.avg_price = (
            pos.avg_price * abs(pos.quantity) + price * abs(signed_qty)
        ) / abs(new_qty)

        pos.quantity = new_qty

    @staticmethod
    def _calculate_realized_pnl(
        pos_qty: Quantity,
        avg_price: Price,
        closing_qty: Quantity,
        fill_price: Price,
    ) -> Cash:
        direction = 1 if pos_qty > 0 else -1
        return closing_qty * (fill_price - avg_price) * direction

    def _apply_cash_update(
        self,
        side: Side,
        qty: Quantity,
        price: Price,
    ) -> None:
        trade_value = qty * price
        if side == Side.BUY:
            self._cash -= trade_value
        else:
            self._cash += trade_value

    def _apply_reduce_or_flip(
        self,
        pos: Position,
        signed_qty: Quantity,
        price: Price,
    ) -> None:
        closing_qty = min(abs(pos.quantity), abs(signed_qty))

        pnl: Cash = self._calculate_realized_pnl(
            pos_qty=pos.quantity,
            avg_price=pos.avg_price,
            closing_qty=closing_qty,
            fill_price=price,
        )

        self._realized_pnl += pnl

        new_qty = pos.quantity + signed_qty

        if pos.quantity * new_qty > 0:
            # Partial close
            pos.quantity = new_qty
        elif new_qty == 0:
            # Fully closed
            pos.quantity = 0
            pos.avg_price = 0.0
        else:
            # Flipped
            pos.quantity = new_qty
            pos.avg_price = price

    def on_fill_sequence(self, fills: Sequence[OrderFillPayload]) -> None:
        for fill in fills:
            self.on_fill(fill=fill)

    def on_fill(self, fill: OrderFillPayload) -> None:
        self._validate_fill(fill=fill)

        order = fill.order
        symbol = order.symbol
        signed_qty = self._signed_quantity(fill=fill)

        pos = self._set_new_position(symbol=symbol)

        if self._is_open_or_add(pos=pos, signed_qty=signed_qty):
            self._apply_open_or_add(
                pos=pos, signed_qty=signed_qty, price=fill.fill_price
            )
        else:
            self._apply_reduce_or_flip(
                pos=pos, signed_qty=signed_qty, price=fill.fill_price
            )

        self._apply_cash_update(
            side=order.side, qty=fill.fill_quantity, price=fill.fill_price
        )

    def close_position(self) -> list[OrderFillPayload]:
        return []
