""" Hertz freerider web scrapper"""
import argparse
import os
import sys
from typing import List

import requests
from bs4 import BeautifulSoup


def match(match_from: List, match_to: List, target_from: str, target_to: str) -> bool:
    """Looksup match data to target data and return bool"""
    if match_from:
        for item in match_from:
            if item.lower() in target_from.lower():
                return True
    if match_to:
        for item in match_to:
            if item.lower() in target_to.lower():
                return True
    return False


def main(arguments):
    """entry point of the script"""
    out_file = f"{os.path.dirname(os.path.abspath(__file__))}/{arguments.out_file}"
    if not arguments.cache:
        print("Fetching data from server", file=sys.stderr)
        res = requests.get(
            "https://www.hertzfreerider.se/unauth/list_transport_offer.aspx"
        )
        if res.status_code != 200:
            return 1

        with open(out_file, "wb") as whandle:
            whandle.write(res.content)

    with open(out_file, "r") as rhandle:
        soup = BeautifulSoup(markup=rhandle, features="html.parser")
        for item in soup.find_all("span", class_="offer_header"):
            locations = item.find_all("a")
            if len(locations) != 2:
                print(f"Weird locations data {locations}")

            from_, to_ = (
                locations[0].text,
                locations[1].text,
            )
            if match(getattr(arguments, "from"), arguments.to, from_, to_):
                print(f"{from_} -- {to_}")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Arguments for Hertz freerider web scrapper"
    )
    parser.add_argument("--cache", action="store_true", help="Use cached data")
    parser.add_argument(
        "--out_file",
        type=str,
        default="out.txt",
        help="Output file path for caching data",
    )
    parser.add_argument("--from", type=str, nargs="+", help="From location")
    parser.add_argument("--to", type=str, nargs="+", help="To location")
    main(parser.parse_args())
