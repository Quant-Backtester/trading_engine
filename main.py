# STL
import logging
import tracemalloc
import argparse

# Custom
from core import setup_engine_logging, Engine


def start_profiling() -> None:
    tracemalloc.start(25)


def end_profiling(logger: logging.Logger) -> None:
    if tracemalloc.is_tracing():
        snapshot = tracemalloc.take_snapshot()
        top = snapshot.statistics("lineno")
        logger.info("Top memory allocation")
        for stat in top:
            logger.info(stat)


def run_engine() -> None:
    setup_engine_logging()
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile-memory", action="store_true")
    args = parser.parse_args()
    logger = logging.getLogger(__name__)

    if args.profile_memory:
        start_profiling()

    engine = Engine()
    engine.run()

    if args.profile_memory:
        end_profiling(logger=logger)


if __name__ == "__main__":
    run_engine()
