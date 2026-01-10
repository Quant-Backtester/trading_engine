# STL
from collections.abc import MutableMapping

from events.payloads import OrderPayload, OrderFillPayload
from common.types import OrderId, Symbol, Cash
from .position import Position
from events.enums import Side

type Positions = MutableMapping[Symbol, Position]


class PositionManager:
    def __init__(self, initial_cash: float = 0.0) -> None:
        self._positions: Positions = {}
        self._cash: Cash = initial_cash
        self._realized_pnl: Cash = 0.0

    def get_position(self, symbol: Symbol) -> Position | None:
        return self._positions.get(symbol)

    def _set_new_position(self, symbol: Symbol) -> Position:
        pos = self.get_position(symbol=symbol)
        if pos is not None:
            return pos
        pos = Position(symbol=symbol)
        self._positions[symbol] = pos
        return self._positions[symbol]

    @property
    def cash(self) -> Cash:
        return self._cash

    @property
    def realized_pnl(self) -> Cash:
        return self._realized_pnl


    def on_fill(self, fill: OrderFillPayload) -> None:
        order: OrderPayload = fill.order
        symbol = order.symbol
        qty = fill.fill_quantity
        price = fill.fill_price

        assert qty > 0
        assert price > 0
        assert isinstance(order.side, Side)

        signed_qty = qty if order.side == Side.BUY else -qty

        pos = self._set_new_position(symbol)

        # Same direction or opening (no pnl update as it is the same direction)
        if pos.quantity == 0 or pos.quantity * signed_qty > 0:
            new_qty = pos.quantity + signed_qty
            pos.avg_price = (
                pos.avg_price * abs(pos.quantity) + price * abs(signed_qty)
            ) / abs(new_qty)
            pos.quantity = new_qty

        # Reduce or flip (updating pnl in this case)
        else:
            closing_qty = min(abs(pos.quantity), abs(signed_qty))

            pnl = closing_qty * (price - pos.avg_price)
            if pos.quantity < 0:
                pnl = -pnl

            self._realized_pnl += pnl

            pos.quantity += signed_qty

            if pos.quantity == 0:
                pos.avg_price = 0.0
            else:
                pos.avg_price = price

        # Cash update (explicit)
        trade_value = qty * price
        if order.side == Side.BUY:
            self._cash -= trade_value
        else:
            self._cash += trade_value

