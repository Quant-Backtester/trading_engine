# STL
from collections.abc import MutableMapping, Sequence
from dataclasses import dataclass, field
import logging

# Custom
from events.event import Event, MarketDataEvent
from events.payloads import OrderFillPayload, MarketDataPayload
from common.types import OrderId, Percentage, Price, Symbol, Cash, Quantity
from common.enums import Side


logger = logging.getLogger("engine")


@dataclass(slots=True)
class SymbolPositionGroup:
    price: Price = 0.0
    positions: dict[OrderId, OrderFillPayload] = field(default_factory=dict)

    def add_new_position(self, position: OrderFillPayload) -> None:
        self.positions[position.order.order_id] = position

    def remove_positon(self, order_id: OrderId) -> OrderFillPayload | None:
        return self.positions.pop(order_id, None)

    @property
    def total_quantity(self) -> Quantity:
        return sum(p.fill_quantity for p in self.positions.values())

    @property
    def avg_price(self) -> Price:
        total_quantity = self.total_quantity
        if total_quantity == 0:
            return 0.0

        return (
            sum(p.fill_quantity * p.fill_price for p in self.positions.values())
            / total_quantity
        )


type PositionMapping = MutableMapping[Symbol, SymbolPositionGroup]


@dataclass(slots=True)
class PositionManager:
    _cash: Cash = 0.0
    _positions: PositionMapping = field(default_factory=dict)
    _realized_pnl: Cash = 0.0

    def __post_init__(self):
        if not isinstance(self._cash, (int, float)):
            self._cash = float(self._cash)

    def get_positions(
        self, symbol: Symbol
    ) -> MutableMapping[OrderId, OrderFillPayload] | None:
        group = self._positions.get(symbol)
        return group.positions if group is not None else None

    def on_market_data(self, md: MarketDataPayload) -> list[OrderFillPayload]:
        group = self._positions.get(md.symbol)
        if group is not None:
            group.price = md.price

        return self.tp_or_sl(md.symbol)

    def on_event(self, event: Event) -> list[OrderFillPayload]:
        if isinstance(event, MarketDataEvent):
            return self.on_market_data(md=event.payload)

        return []

    @property
    def cash(self) -> Cash:
        return self._cash

    @property
    def realized_pnl(self) -> Cash:
        return self._realized_pnl

    @property
    def total_unrealized_pnl(self) -> Cash:
        return sum(
            self._calculate_unrealized_pnl_for_group(group)
            for group in self._positions.values()
        )

    @staticmethod
    def _validate_fill(fill: OrderFillPayload) -> None:
        assert fill.fill_quantity > 0, "Fill quantity must be positive"
        assert fill.fill_price > 0, "Fill price must be positive"
        assert isinstance(fill.order.side, Side)

    @staticmethod
    def _signed_quantity(fill: OrderFillPayload) -> Quantity:
        return (
            fill.fill_quantity
            if fill.order.side == Side.BUY
            else -fill.fill_quantity
        )

    def _get_or_create_group(self, symbol: Symbol) -> SymbolPositionGroup:
        if symbol not in self._positions:
            self._positions[symbol] = SymbolPositionGroup()
        return self._positions[symbol]

    def _calculate_unrealized_pnl_for_group(
        self, group: SymbolPositionGroup
    ) -> Cash:
        if group.total_quantity == 0:
            return 0.0
        return group.total_quantity * (group.price - group.avg_price)

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
        self, side: Side, qty: Quantity, price: Price
    ) -> None:
        trade_value = qty * price
        if side == Side.BUY:
            self._cash -= trade_value
        else:
            self._cash += trade_value

    def on_fill(self, fill: OrderFillPayload) -> None:
        self._validate_fill(fill=fill)

        order = fill.order
        symbol = order.symbol

        group = self._get_or_create_group(symbol=symbol)

        group.add_new_position(fill)

        self._apply_cash_update(
            side=order.side, qty=fill.fill_quantity, price=fill.fill_price
        )

        logger.info("filled order %s", OrderFillPayload)

    def on_fill_sequence(self, fills: Sequence[OrderFillPayload]) -> None:
        for fill in fills:
            self.on_fill(fill)

    def close_position(
        self, symbol: Symbol, order_id: OrderId
    ) -> OrderFillPayload | None:
        group = self._positions.get(symbol)
        if group is None:
            return

        return self._positions[symbol].remove_positon(order_id=order_id)

    def close_positions(self, symbol: Symbol) -> list[OrderFillPayload]:
        group = self._positions.get(symbol)
        if group is None:
            return []
        closed = list(group.positions.values())
        self._positions.pop(symbol, None)
        return closed

    def get_net_position(self, symbol: Symbol) -> dict[str, float]:
        group = self._positions.get(symbol)
        if not group or group.total_quantity == 0:
            return {
                "quantity": 0.0,
                "avg_price": 0.0,
                "current_price": 0.0,
                "unrealized_pnl": 0.0,
            }

        return {
            "quantity": group.total_quantity,
            "avg_price": group.avg_price,
            "current_price": group.price,
            "unrealized_pnl": self._calculate_unrealized_pnl_for_group(
                group=group
            ),
        }

    def _handle_take_profit(
        self, current_price: Price, position: OrderFillPayload
    ) -> OrderFillPayload | None:
        take_profit_price = position.order.take_profit
        order_id = position.order.order_id
        if not take_profit_price:
            return None
        if (
            position.order.side == Side.BUY
            and current_price >= take_profit_price
        ) or (
            position.order.side == Side.SELL
            and current_price <= take_profit_price
        ):
            logger.info(
                f"Take profit triggered for order {order_id} at price {current_price}"
            )
            return self.close_position(
                symbol=position.order.symbol, order_id=order_id
            )

        return None

    def _handle_stop_loss(
        self, current_price: Price, position: OrderFillPayload
    ) -> OrderFillPayload | None:
        order_id = position.order.order_id
        if not position.order.stop_loss:
            return None
        if (
            position.order.side == Side.BUY
            and current_price <= position.order.stop_loss
        ) or (
            position.order.side == Side.SELL
            and current_price >= position.order.stop_loss
        ):
            logger.info(
                f"Stop loss triggered for order {order_id} at price {current_price}"
            )
            return self.close_position(
                symbol=position.order.symbol, order_id=order_id
            )

        return None

    def tp_or_sl(self, symbol: Symbol) -> list[OrderFillPayload]:
        position_group = self._positions.get(symbol)
        if not position_group or position_group.total_quantity == 0:
            return []

        closed_positions = []

        for _, position in list(position_group.positions.items()):
            current_price = position_group.price

            if tp_order := self._handle_take_profit(
                current_price=current_price, position=position
            ):
                closed_positions.append(tp_order)

            if sl_order := self._handle_stop_loss(
                current_price=current_price, position=position
            ):
                closed_positions.append(sl_order)

        return closed_positions
