# STL
import argparse
from argparse import Namespace

# third party
import yfinance as yf
import pandas as pd


def main(args: Namespace):
    data = yf.download(
        tickers=args.symbol,
        start="2015-01-01",
        end="2023-12-31",
        multi_level_index=False,
    )

    if data is None:
        print("data is None")
        return

    data.to_csv(f"data/{args.symbol}.csv")
    print(f"Saved {len(data)} rows to aapl_data.csv")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--symbol", type=str, required=True)
    args: Namespace = parser.parse_args()
    main(args=args)
