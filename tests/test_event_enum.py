import unittest
from common.enums import EventEnum


class TestEventEnum(unittest.TestCase):
    def test_enum_values_are_unique(self):
        values = [e.value for e in EventEnum]
        self.assertEqual(len(values), len(set(values)))

    def test_expected_event_types_exist(self):
        expected = {
            "market_data",
            "order_submit",
            "order_fill",
            "order_cancel",
            "timer",
        }
        actual = {e.value for e in EventEnum}
        self.assertEqual(actual, expected)

    def test_enum_string_conversion(self):
        self.assertEqual(str(EventEnum.MARKET_DATA), "market_data")


if __name__ == "__main__":
    unittest.main()
