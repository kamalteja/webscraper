#!/usr/bin/env python3
""" Hertz freerider web scrapper"""

import os

import requests_cache

from freerider.arguments import rider_arguments
from freerider.hertz.hertz import hertz_rides

requests_cache.install_cache(
    f"{os.path.dirname(os.path.dirname(os.path.abspath(__file__)))}/webscrapper",
    expire_after=60 * 60,
)


def main(arguments):
    """Runs all the freerider plugins"""
    for plugin in [hertz_rides]:
        plugin(arguments)


if __name__ == "__main__":
    main(rider_arguments())