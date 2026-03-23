# STL
import logging
import argparse
from argparse import _SubParsersAction

# Custom
from core import setup_engine_logging, Engine
from market_data.replayer import MarketDataReplayer
from market_data import CSVMarketDataSource


def config_csv_parser(
    subparser: _SubParsersAction[argparse.ArgumentParser],
) -> None:
    csv_parser = subparser.add_parser("csv", help="Process CSV file")
    csv_parser.add_argument("--path", required=True, help="Path to CSV file")


def config_db_parser(
    subparser: _SubParsersAction[argparse.ArgumentParser],
) -> None:
    db_parser = subparser.add_parser("db", help="Use database")
    db_parser.add_argument("--host", default="localhost")
    db_parser.add_argument("--port", default=5432)


def config_json_paser(
    subparser: _SubParsersAction[argparse.ArgumentParser],
) -> None:
    pass


def config_helper_argument(
    parser: argparse.ArgumentParser,
) -> None:
    parser.add_argument("--profile-memory", action="store_true")


def config_engine_argument(
    parser: argparse.ArgumentParser,
) -> None:
    parser.add_argument(
        "-c", "--cash", type=int, help="Your initial trading capital"
    )


def main() -> None:
    """later on, the engine can be running in the memory (redis/vulkey)"""
    setup_engine_logging(level=logging.INFO)
    parser = argparse.ArgumentParser()

    config_engine_argument(parser=parser)
    config_helper_argument(parser=parser)

    subparser: _SubParsersAction[argparse.ArgumentParser] = (
        parser.add_subparsers(dest="mode", required=True, help="Operation mode")
    )

    config_csv_parser(subparser=subparser)
    config_db_parser(subparser=subparser)

    args = parser.parse_args()

    engine = Engine(initial_cash=args.cash)
    replayer = MarketDataReplayer()
    if args.mode == "csv":
        replayer.set_market_data_source(
            source=CSVMarketDataSource(path=args.path)
        )
    elif args.mode == "db":
        # fetch data from the database
        pass
    elif args.mode == "json":
        # json handler
        pass
    
    replayer.replay(engine=engine, chunked=True)


if __name__ == "__main__":
    main()
