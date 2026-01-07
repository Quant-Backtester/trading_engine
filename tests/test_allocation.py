from core import Engine
import unittest



class TestMemoryStability(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = Engine()

    def test_engine_memory(self):
        import tracemalloc
        tracemalloc.start()

        self.engine.run()

        current, peak = tracemalloc.get_traced_memory()
        self.assertLess(peak, 200 * 1024 * 1024)
