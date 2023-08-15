import argparse


def rider_arguments(cli_args=None) -> argparse.Namespace:
    """Defines arguments for freerider scrapper"""
    parser = argparse.ArgumentParser(
        description="Arguments for Hertz freerider web scrapper"
    )
    parser.add_argument(
        "--out_file",
        type=str,
        default="out.html",
        help="Output file path for caching data",
    )
    parser.add_argument(
        "--from", dest="from_", type=str, nargs="+", help="From location"
    )
    parser.add_argument("--to", type=str, nargs="+", help="To location")
    parser.add_argument("-s", "--station", type=str, nargs="+", help="To location")
    return parser.parse_args(cli_args) if cli_args else parser.parse_args()
