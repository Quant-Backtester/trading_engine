import unittest
from clock import Clock


class TestClock(unittest.TestCase):
    def setUp(self) -> None:
        self.clock = Clock()

    def test_initial_state(self) -> None:
        self.assertEqual(first=self.clock.now, second=0)

    def test_advance_to(self) -> None:
        self.clock.advance_to(timestamp=10)
        self.assertEqual(first=self.clock.now, second=10)

        self.clock.advance_to(timestamp=25)
        self.assertEqual(first=self.clock.now, second=25)

    def test_duplicated_timestamp(self) -> None:
        self.clock.advance_to(timestamp=10)
        self.clock.advance_to(timestamp=10)
        self.assertEqual(first=self.clock.now, second=10)

    def test_advance_to_reject(self) -> None:
        self.clock.advance_to(timestamp=10)

        with self.assertRaises(expected_exception=ValueError):
            self.clock.advance_to(timestamp=9)

    def test_now_readonly(self) -> None:
        with self.assertRaises(expected_exception=AttributeError):
            self.clock.now = 100  # type: ignore

    def test_deterministic_across_instances(self):
        c2 = Clock()
        self.clock.advance_to(timestamp=50)
        c2.advance_to(timestamp=50)
        self.assertEqual(first=self.clock.now, second=c2.now)


if __name__ == "__main__":
    unittest.main()
