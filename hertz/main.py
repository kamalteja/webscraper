""" Hertz freerider web scrapper"""
import argparse
import os
import re
import sys
from abc import abstractmethod
from typing import List

import bs4
import requests

HERTZ_FREE_RIDER_URL = "https://www.hertzfreerider.se/unauth/list_transport_offer.aspx"
DATA_LIST = "ctl00_ContentPlaceHolder1_Display_transport_offer_advanced1_DataList1"


class RideFromTo:
    """Represents from - to data format"""

    def __init__(self, from_, to_):
        self.from_ = from_
        self.to_ = to_

    def __str__(self) -> str:
        if not self.from_ or not self.from_:
            return ""
        return f"{self.from_} - {self.to_}"

    @classmethod
    @abstractmethod
    def parse_from_to(cls, data: bs4.element.Tag):
        """parse from - to data"""


class DateFromTo(RideFromTo):
    """Represents date data"""

    @classmethod
    def parse_from_to(cls, data: bs4.element.Tag):
        """Parses date data"""
        try:
            return cls(
                from_=data.find(
                    "span", id=re.compile(rf"{DATA_LIST}_ctl[0-9]+_offerDate")
                ).text,
                to_=data.find(
                    "span", id=re.compile(rf"{DATA_LIST}_ctl[0-9]+_Label1")
                ).text,
            )
        except AttributeError:
            return cls("", "")


class StationFromTo(RideFromTo):
    """Represents Station from - to data"""

    @classmethod
    def parse_from_to(cls, data: bs4.element.Tag):
        """Parses date data"""
        span = data.find("span", class_="offer_header")
        if not span:
            raise ValueError("Unsupported tag received in {cls}")

        locations = span.find_all("a")
        if len(locations) != 2:
            print(f"Weird locations data {locations}")
            raise ValueError("Unsupported tag received in {cls}")

        return cls(
            from_=locations[0].text,
            to_=locations[1].text,
        )


class Ride:
    """Represents ride information"""

    def __init__(self, data: bs4.element.Tag):
        self._data = data

    def __str__(self) -> str:
        return f"{self.station} ({self.car})\n    {self.date}"

    @property
    def car(self) -> str:
        """Return car type"""
        try:
            return self._data.find(
                "span", id=re.compile(rf"{DATA_LIST}_ctl[0-9]+_offerDescription1")
            ).text
        except AttributeError:
            pass
        return ""

    @property
    def date(self) -> DateFromTo:
        """Returns data from - to"""
        return DateFromTo.parse_from_to(self._data)

    @property
    def station(self) -> StationFromTo:
        """Returns station from - to"""
        return StationFromTo.parse_from_to(self._data)


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


def get_soup_data(soup: bs4.BeautifulSoup, tag: str, **params):
    """Finds tag in soup and yields the result"""
    data = soup.find(tag, **params)
    if data:
        yield from data


def main(arguments):
    """entry point of the script"""
    out_file = f"{os.path.dirname(os.path.abspath(__file__))}/{arguments.out_file}"
    if not arguments.cache:
        print("Fetching data from server", file=sys.stderr)
        res = requests.get(HERTZ_FREE_RIDER_URL)
        if res.status_code != 200:
            return 1

        with open(out_file, "wb") as whandle:
            whandle.write(res.content)

    with open(out_file, "r") as rhandle:
        soup = bs4.BeautifulSoup(markup=rhandle, features="html.parser")
        for item in get_soup_data(
            soup,
            "table",
            id=DATA_LIST,
        ):
            if not str(item).strip():
                continue

            ride = Ride(item)

            if match(
                getattr(arguments, "from"),
                arguments.to,
                ride.station.from_,
                ride.station.to_,
            ):
                print(ride)
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Arguments for Hertz freerider web scrapper"
    )
    parser.add_argument("--cache", action="store_true", help="Use cached data")
    parser.add_argument(
        "--out_file",
        type=str,
        default="out.html",
        help="Output file path for caching data",
    )
    parser.add_argument("--from", type=str, nargs="+", help="From location")
    parser.add_argument("--to", type=str, nargs="+", help="To location")
    main(parser.parse_args())
