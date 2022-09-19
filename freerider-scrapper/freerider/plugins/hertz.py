""" Hertz freerider web scrapper"""
import re
from abc import abstractmethod
from typing import List, NamedTuple

import bs4
import requests
from freerider.arguments import rider_arguments

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
        from_ = data.find("span", id=re.compile(rf"{DATA_LIST}_ctl[0-9]+_offerDate"))
        to_ = data.find("span", id=re.compile(rf"{DATA_LIST}_ctl[0-9]+_Label1"))

        return cls(
            from_=from_.next if from_ else "",
            to_=to_.next if to_ else "",
        )


class StationFromTo(RideFromTo):
    """Represents Station from - to data"""

    @classmethod
    def parse_from_to(cls, data: bs4.element.Tag):
        """Parses date data"""
        span = data.find("span", class_="offer_header")
        if not span or not isinstance(span, bs4.element.Tag):
            raise ValueError("Unsupported tag received in {cls}")

        locations = span.find_all("a")
        if len(locations) != 2:
            print(f"Weird locations data {locations}")
            raise ValueError("Unsupported tag received in {cls}")

        return cls(
            from_=locations[0].text,
            to_=locations[1].text,
        )


class Ride(NamedTuple):
    """Represents ride information"""

    car: str
    date: DateFromTo
    station: StationFromTo

    def __str__(self) -> str:
        return f"------\n{self.station} ({self.car})\n{self.date}"

    @classmethod
    def parse_ride(cls, data: bs4.element.Tag):
        """Parser for ride data"""
        _car = data.find(
            "span", id=re.compile(rf"{DATA_LIST}_ctl[0-9]+_offerDescription1")
        )

        return cls(
            car=_car.text if _car else "",
            date=DateFromTo.parse_from_to(data),
            station=StationFromTo.parse_from_to(data),
        )


def match_to_from(match_from: List, match_to: List, ride: Ride) -> bool:
    """Looksup to-from match data to target data and return bool"""
    if match_from:
        for item in match_from:
            if item.lower() in ride.station.from_.lower():
                return True
    if match_to:
        for item in match_to:
            if item.lower() in ride.station.to_.lower():
                return True
    return False


def match_station(match_station_: List[str], ride: Ride):
    """Looksup match station to target station and returns bool"""
    return match_to_from(match_from=match_station_, match_to=match_station_, ride=ride)


def get_soup_data(soup: bs4.BeautifulSoup, tag: str, **params):
    """Finds tag in soup and yields the result"""
    data = soup.find(tag, **params)
    if data:
        yield from data


def hertz_rides(arguments):
    """entry point of the script"""
    res = requests.get(HERTZ_FREE_RIDER_URL)
    if res.status_code != 200:
        return 1

    soup = bs4.BeautifulSoup(markup=res.content, features="html.parser")
    for item in get_soup_data(
        soup,
        "table",
        id=DATA_LIST,
    ):
        if not str(item).strip():
            continue

        ride = Ride.parse_ride(item)

        if (
            (not arguments.from_ and not arguments.to and not arguments.station)
            or match_to_from(arguments.from_, arguments.to, ride)
            or match_station(arguments.station, ride)
        ):
            print(ride)
    return 0


if __name__ == "__main__":
    hertz_rides(rider_arguments())
