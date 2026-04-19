"""Regression tests for the cash-aware fill clamp.

Before this fix, PositionManager.on_fill let _cash go arbitrarily
negative — a DCA strategy starting with $10k on AAPL could accumulate
$57M of phantom P/L because every "buy 100 shares" signal filled
regardless of balance. These tests pin the new behavior:

  - full fill when cash is sufficient
  - size-down fill when cash covers only part of the order
  - skip entirely when cash is non-positive
  - SELL orders are unaffected (no buying-power check on close)
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


class TestBuyClamp:
  def test_full_fill_when_cash_sufficient(self):
    pm = PositionManager(_cash=10_000.0)
    pm.on_fill(_make_fill(side=Side.BUY, qty=10, price=100))
    assert pm.cash == 9_000.0
    group = pm._positions["AAPL"]
    assert group.total_quantity == 10

  def test_size_down_when_partial_affordable(self):
    """Buy 100 shares of $100 stock on $1,500 cash → fill 15 shares."""
    pm = PositionManager(_cash=1_500.0)
    pm.on_fill(_make_fill(side=Side.BUY, qty=100, price=100))
    # Cash spent exactly — nothing left over.
    assert math.isclose(pm.cash, 0.0, abs_tol=1e-6)
    group = pm._positions["AAPL"]
    assert math.isclose(group.total_quantity, 15.0, abs_tol=1e-6)

  def test_skip_when_cash_zero(self):
    pm = PositionManager(_cash=0.0)
    pm.on_fill(_make_fill(side=Side.BUY, qty=10, price=100))
    assert pm.cash == 0.0
    assert "AAPL" not in pm._positions

  def test_skip_when_cash_negative(self):
    """Paranoia: ledger should never reach this state post-fix, but
    if it does (e.g. closing trades at a loss below zero), never
    let a subsequent BUY make it worse."""
    pm = PositionManager(_cash=-50.0)
    pm.on_fill(_make_fill(side=Side.BUY, qty=10, price=100))
    assert pm.cash == -50.0
    assert "AAPL" not in pm._positions

  def test_cash_never_goes_negative_on_repeated_dca_style_buys(self):
    """DCA-style regression: fire "buy 10 shares of $100" every bar
    on $100 cash. Only the first bar fills (1 share). All later bars
    are skipped, cash stays at 0, position stops growing."""
    pm = PositionManager(_cash=100.0)
    for i in range(20):
      pm.on_fill(
        _make_fill(side=Side.BUY, qty=10, price=100, order_id=i + 1)
      )
    assert pm.cash >= 0.0
    assert math.isclose(pm.cash, 0.0, abs_tol=1e-6)
    group = pm._positions["AAPL"]
    assert math.isclose(group.total_quantity, 1.0, abs_tol=1e-6)


class TestSellUnaffected:
  def test_sell_adds_cash_without_clamp(self):
    """SELL orders are closing positions, not opening — buying-power
    checks don't apply. Verify the clamp path leaves them alone."""
    pm = PositionManager(_cash=10_000.0)
    # Open a long first so the sell has something to close.
    pm.on_fill(
      _make_fill(side=Side.BUY, qty=10, price=100, order_id=1)
    )
    assert pm.cash == 9_000.0
    # Now SELL at a higher price — cash should rise by full proceeds.
    pm.on_fill(
      _make_fill(side=Side.SELL, qty=10, price=120, order_id=2)
    )
    assert pm.cash == 9_000.0 + 10 * 120
