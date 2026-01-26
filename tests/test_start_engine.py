import unittest

from core.engine import Engine
from market_data.replayer import MarketDataReplayer
from events.event import Event
from events.payloads import MarketDataPayload
from common.enums import EventEnum
from market_data import FakeMarketDataSource
from strategies import DummyStrategy




class TestName(unittest.TestCase):
    def test_market_data_replay_and_dispatch(self):
        # Arrange
        records = [
            MarketDataPayload(timestamp=1, symbol="AAPL", price=100.0, volume=10),
            MarketDataPayload(timestamp=2, symbol="AAPL", price=101.0, volume=5),
            MarketDataPayload(timestamp=3, symbol="AAPL", price=102.0, volume=8),
        ]

        source = FakeMarketDataSource(records)
        replayer = MarketDataReplayer()
        replayer.set_market_data_source(source=source)
        engine = Engine()

        strategy = DummyStrategy()
        engine.register_strategy(strategy)

        # Act
        replayer.replay(engine)
        engine.run()

        self.assertEqual(len(strategy.events), 3)
        timestamps = [event.timestamp for event in strategy.events]
        self.assertEqual(timestamps, [1, 2, 3])
        event_types = [e.event_type for e in strategy.events]
        self.assertTrue(all(t == EventEnum.MARKET_DATA for t in event_types))

        self.assertEqual(engine._clock.now, 3)

    def setUp(self) -> None:
        return super().setUp()

    def tearDown(self) -> None:
        return super().tearDown()

    @classmethod
    def setUpClass(cls) -> None:
        return super().setUpClass()

    @classmethod
    def tearDownClass(cls) -> None:
        return super().tearDownClass()


if __name__ == "__main__":
    unittest.main()


