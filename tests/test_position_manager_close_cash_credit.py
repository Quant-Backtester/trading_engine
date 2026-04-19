"""Regression tests for cash credit on position close.

Before this fix, close_position (TP/SL path) and close_position_fifo
(CloseSignal path) updated positions and _realized_pnl but never called
_apply_cash_update. Cash stayed at the post-buy balance (often ~0) and
_clamp_buy_fill_to_cash silently rejected every subsequent BUY — so a
mean-reversion strategy with RSI<30 buys / RSI>70 sells would trade
once in year 1 and then go silent for the rest of the backtest.
"""
# STL
import math

# Custom
from common.enums import OrderType, Side
from core.position_manager import PositionManager
from events.payloads import OrderPayload, OrderFillPayload


def _make_fill(
    *, side: Side, qty: float, price: float, order_id: int = 1
) -> OrderFillPayload:
    order = OrderPayload(
        timestamp=0,
        order_id=order_id,
        symbol="AAPL",
        side=side,
        quantity=qty,
        order_type=OrderType.MARKET,
        price=price,
    )
    return OrderFillPayload(
        order=order,
        fill_timestamp=0,
        fill_price=price,
        fill_quantity=qty,
        remaining_quantity=0,
    )


class TestCloseFifoCreditsCash:
    def test_full_close_credits_cash_at_current_price(self):
        pm = PositionManager(_cash=10_000.0)
        pm.on_fill(_make_fill(side=Side.BUY, qty=10, price=100))
        assert pm.cash == 9_000.0
        # Mark the group at a higher price and close.
        pm._positions["AAPL"].price = 120.0
        closed = pm.close_position_fifo(symbol="AAPL")
        assert len(closed) == 1
        assert math.isclose(pm.cash, 9_000.0 + 10 * 120.0, abs_tol=1e-6)
        assert "AAPL" not in pm._positions
        assert math.isclose(pm.realized_pnl, 10 * (120.0 - 100.0), abs_tol=1e-6)

    def test_partial_fraction_close_credits_proportional_cash(self):
        pm = PositionManager(_cash=10_000.0)
        pm.on_fill(_make_fill(side=Side.BUY, qty=10, price=100))
        pm._positions["AAPL"].price = 150.0
        pm.close_position_fifo(symbol="AAPL", fraction=0.5)
        # Half closed → credit 5 × 150 = 750
        assert math.isclose(pm.cash, 9_000.0 + 5 * 150.0, abs_tol=1e-6)
        # Remainder still open
        assert math.isclose(
            pm._positions["AAPL"].total_quantity, 5.0, abs_tol=1e-6
        )

    def test_partial_quantity_close_credits_exact_cash(self):
        pm = PositionManager(_cash=10_000.0)
        pm.on_fill(_make_fill(side=Side.BUY, qty=10, price=100))
        pm._positions["AAPL"].price = 110.0
        pm.close_position_fifo(symbol="AAPL", quantity=3)
        assert math.isclose(pm.cash, 9_000.0 + 3 * 110.0, abs_tol=1e-6)
        assert math.isclose(
            pm._positions["AAPL"].total_quantity, 7.0, abs_tol=1e-6
        )

    def test_round_trip_leaves_cash_at_initial_plus_realized(self):
        """Buy 10@100, sell all @120 → cash should be 10000 + 200 = 10200.
        Pre-fix this returned 0 because close_position_fifo never credited.
        """
        pm = PositionManager(_cash=10_000.0)
        pm.on_fill(_make_fill(side=Side.BUY, qty=10, price=100))
        pm._positions["AAPL"].price = 120.0
        pm.close_position_fifo(symbol="AAPL")
        assert math.isclose(pm.cash, 10_200.0, abs_tol=1e-6)

    def test_multiple_round_trips_accumulate_cash(self):
        """Simulates the RSI-mean-reversion scenario: multiple full
        round-trips should each credit proceeds so later buys can fire."""
        pm = PositionManager(_cash=10_000.0)
        # Round 1: 10@100 → 10@110
        pm.on_fill(_make_fill(side=Side.BUY, qty=10, price=100, order_id=1))
        pm._positions["AAPL"].price = 110.0
        pm.close_position_fifo(symbol="AAPL")
        # Round 2 should be fundable at current cash.
        assert pm.cash > 0
        pm.on_fill(_make_fill(side=Side.BUY, qty=10, price=110, order_id=2))
        pm._positions["AAPL"].price = 125.0
        pm.close_position_fifo(symbol="AAPL")
        # 10000 + (10*110 - 10*100) + (10*125 - 10*110) = 10250
        assert math.isclose(pm.cash, 10_250.0, abs_tol=1e-6)


class TestClosePositionCreditsCash:
    def test_tp_sl_close_credits_cash(self):
        """close_position is the TP/SL path; same cash-credit bug applied."""
        pm = PositionManager(_cash=10_000.0)
        pm.on_fill(_make_fill(side=Side.BUY, qty=10, price=100, order_id=7))
        pm._positions["AAPL"].price = 115.0
        pm.close_position(symbol="AAPL", order_id=7)
        assert math.isclose(pm.cash, 9_000.0 + 10 * 115.0, abs_tol=1e-6)
