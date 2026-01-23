# STL
import logging
import argparse
from argparse import _SubParsersAction

# Custom
from core import setup_engine_logging, Engine
from market_data.replayer import MarketDataReplayer


def config_csv_parser(
    subparser: _SubParsersAction[argparse.ArgumentParser],
) -> None:
    csv_parser = subparser.add_parser("csv", help="Process CSV file")
    csv_parser.add_argument("--path", required=True, help="Path to CSV file")
    csv_parser.add_argument("--profile-memory", action="store_true")


def config_db_parser(
    subparser: _SubParsersAction[argparse.ArgumentParser],
) -> None:
    db_parser = subparser.add_parser("db", help="Use database")
    db_parser.add_argument("--host", default="localhost")
    db_parser.add_argument("--port", default=5432)


def config_profiler(
    parser: argparse.ArgumentParser,
) -> None:
    parser.add_argument("--profile-memory", action="store_true")


def config_engine_argument(
    parser: argparse.ArgumentParser,
) -> None:
    parser.add_argument("cash", type=int, required=True)


def run_engine() -> None:
    """later on, the engine can be running in the memory (redis/vulkey)"""
    setup_engine_logging()
    parser = argparse.ArgumentParser()

    config_engine_argument(parser=parser)
    config_profiler(parser=parser)

    subparser: _SubParsersAction[argparse.ArgumentParser] = (
        parser.add_subparsers(dest="mode", required=True, help="Operation mode")
    )

    config_csv_parser(subparser=subparser)
    config_db_parser(subparser=subparser)

    args = parser.parse_args()
    logger = logging.getLogger(__name__)

    engine = Engine(initial_cash=args.cash)
    # replayer = MarketDataReplayer()


if __name__ == "__main__":
    run_engine()
