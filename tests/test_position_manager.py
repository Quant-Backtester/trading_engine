import unittest

# Custom imports (adjust paths as needed)
from core.position_manager import PositionManager
from core.position import Position
from events.payloads import OrderPayload, OrderFillPayload, MarketDataPayload
from common.enums import Side


class TestPositionManager(unittest.TestCase):
    def setUp(self) -> None:
        self.pm = PositionManager(initial_cash=10_000.0)
        self.symbol = "AAPL"
        self._order_id = 1

    def _next_order_id(self) -> int:
        oid = self._order_id
        self._order_id += 1
        return oid

    def _buy(self, qty: int, price: float) -> None:
        order = OrderPayload(
            order_id=self._next_order_id(),
            symbol=self.symbol,
            side=Side.BUY,
            quantity=qty,
        )
        fill = OrderFillPayload(
            order=order,
            fill_quantity=qty,
            fill_price=price,
        )
        self.pm.on_fill(fill)

    def _sell(self, qty: int, price: float) -> None:
        order = OrderPayload(
            order_id=self._next_order_id(),
            symbol=self.symbol,
            side=Side.SELL,
            quantity=qty,
        )
        fill = OrderFillPayload(
            order=order,
            fill_quantity=qty,
            fill_price=price,
        )
        self.pm.on_fill(fill)

    def test_open_long_position(self):
        self._buy(10, 100.0)

        pos = self.pm.get_position(self.symbol)
        self.assertIsNotNone(pos)
        self.assertEqual(pos.quantity, 10)  # type: ignore
        self.assertEqual(pos.avg_price, 100.0)  # type: ignore
        self.assertEqual(self.pm.cash, 9_000.0)
        self.assertEqual(self.pm.realized_pnl, 0.0)

    def test_add_to_long_position(self):
        self._buy(10, 100.0)
        self._buy(10, 110.0)

        pos = self.pm.get_position(self.symbol)
        self.assertIsNotNone(pos)
        self.assertEqual(pos.quantity, 20)  # type: ignore
        self.assertAlmostEqual(pos.avg_price, 105.0)  # type: ignore
        self.assertEqual(self.pm.cash, 7_900.0)
        self.assertEqual(self.pm.realized_pnl, 0.0)

    def test_partial_close_long(self):
        self._buy(10, 100.0)
        self._sell(4, 110.0)

        pos = self.pm.get_position(self.symbol)
        self.assertIsNotNone(pos)
        self.assertEqual(pos.quantity, 6)  # type: ignore
        self.assertEqual(pos.avg_price, 100.0)  # type: ignore

        # Realized PnL = 4 * (110 - 100)
        self.assertEqual(self.pm.realized_pnl, 40.0)
        self.assertEqual(self.pm.cash, 10_000.0 - 1000.0 + 440.0)

    def test_full_close_long(self):
        self._buy(10, 100.0)
        self._sell(10, 110.0)

        pos = self.pm.get_position(self.symbol)
        self.assertIsNotNone(pos)
        self.assertEqual(pos.quantity, 0)  # type: ignore
        self.assertEqual(pos.avg_price, 0.0)  # type: ignore

        self.assertEqual(self.pm.realized_pnl, 100.0)
        self.assertEqual(self.pm.cash, 10_100.0)

    def test_flip_long_to_short(self):
        self._buy(10, 100.0)
        self._sell(15, 110.0)

        pos = self.pm.get_position(self.symbol)
        self.assertIsNotNone(pos)
        self.assertEqual(pos.quantity, -5)  # type: ignore
        self.assertEqual(pos.avg_price, 110.0)  # type: ignore

        # Closed 10 shares at +10 profit
        self.assertEqual(self.pm.realized_pnl, 100.0)

        # Cash: -1000 + 1650
        self.assertEqual(self.pm.cash, 10_650.0)

    def test_open_short_position(self):
        self._sell(10, 200.0)

        pos = self.pm.get_position(self.symbol)
        self.assertIsNotNone(pos)
        self.assertEqual(pos.quantity, -10)  # type: ignore
        self.assertEqual(pos.avg_price, 200.0)  # type: ignore
        self.assertEqual(self.pm.cash, 12_000.0)
        self.assertEqual(self.pm.realized_pnl, 0.0)

    def test_partial_cover_short(self):
        self._sell(10, 200.0)
        self._buy(4, 180.0)

        pos = self.pm.get_position(self.symbol)
        self.assertIsNotNone(pos)
        self.assertEqual(pos.quantity, -6)  # type: ignore
        self.assertEqual(pos.avg_price, 200.0)  # type: ignore

        # Profit: 4 * (200 - 180)
        self.assertEqual(self.pm.realized_pnl, 80.0)
        self.assertEqual(self.pm.cash, 12_000.0 - 720.0)

    def test_flip_short_to_long(self):
        self._sell(10, 200.0)
        self._buy(15, 180.0)

        pos = self.pm.get_position(self.symbol)
        self.assertIsNotNone(pos)
        self.assertEqual(pos.quantity, 5)  # type: ignore
        self.assertEqual(pos.avg_price, 180.0)  # type: ignore

        # Closed 10 shares at +20 profit
        self.assertEqual(self.pm.realized_pnl, 200.0)

        # Cash: +2000 - 2700
        self.assertEqual(self.pm.cash, 9_300.0)

    def test_gain(self):
        self._buy(15, 200)
        self._sell(15, 201)

        self.assertEqual(self.pm.cash, 10015)
        self.assertEqual(self.pm.realized_pnl, 15)

    def test_lost(self):
        self._buy(15, 200)
        self._sell(15, 199)

        self.assertEqual(self.pm.cash, 9985)
        self.assertEqual(self.pm.realized_pnl, -15)

    def test_unrealized_pnl_buy(self):
        self._buy(10, 200)

        update = MarketDataPayload(
            symbol="AAPL", timestamp=1, price=210, volume=10000
        )
        self.pm.on_market_data(update)
        self.assertEqual(self.pm.total_unrealized_pnl, 100)

    def test_unrealized_pnl_sell(self):
        self._sell(10, 200)

        update = MarketDataPayload(
            symbol="AAPL", timestamp=1, price=190, volume=10000
        )
        self.pm.on_market_data(update)
        self.assertEqual(self.pm.total_unrealized_pnl, 100)


if __name__ == "__main__":
    unittest.main()
