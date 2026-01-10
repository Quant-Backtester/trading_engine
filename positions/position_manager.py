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
        fill_qty = fill.fill_quantity
        fill_price = fill.fill_price

        signed_qty = fill_qty if order.side == Side.BUY else -fill_qty

        pos = self._set_new_position(symbol=symbol)

        if (
            pos.quantity == 0
            or (pos.quantity > 0 and signed_qty > 0)
            or (pos.quantity < 0 and signed_qty < 0)
        ):
            new_qty = pos.quantity + signed_qty
            pos.avg_price = (
                pos.avg_price * abs(pos.quantity) + fill_price * abs(signed_qty)
            ) / abs(new_qty)
            pos.quantity = new_qty

        else:
            closing_qty = min(abs(pos.quantity), abs(signed_qty))
            pnl = (
                closing_qty
                * (fill_price - pos.avg_price)
                * (1 if pos.quantity > 0 else -1)
            )
            self._realized_pnl += pnl

            pos.quantity += signed_qty

            if pos.quantity == 0:
                pos.avg_price = 0.0
            else:
                pos.avg_price = fill_price

        self._cash -= signed_qty * fill_price
