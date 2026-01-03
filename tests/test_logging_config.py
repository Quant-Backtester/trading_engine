import logging
import unittest
from core import setup_engine_logging


class TestLogging(unittest.TestCase):
    def test_setup_logging(self) -> None:
        try:
            setup_engine_logging(level=logging.INFO)
        except Exception as e:
            self.fail(f"Logging setup raised exception: {e}")


    def setUp(self) -> None:
        return super().setUp()

    def tearDown(self) -> None:
        logging.shutdown()
    @classmethod
    def setUpClass(cls) -> None:
        return super().setUpClass()

    @classmethod
    def tearDownClass(cls) -> None:
        return super().tearDownClass()


if __name__ == "__main__":
    unittest.main()

# @description

