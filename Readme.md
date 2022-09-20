# Freerider scrapper
A web scrapper module that parses freerider (hertz) page and prints available cars according to the supplied filters.

## Usage
```bash
frider.py --help
usage: frider.py [-h] [--out_file OUT_FILE] [--from FROM_ [FROM_ ...]] [--to TO [TO ...]] [-s STATION [STATION ...]]

Arguments for Hertz freerider web scrapper

options:
  -h, --help            show this help message and exit
  --out_file OUT_FILE   Output file path for caching data
  --from FROM_ [FROM_ ...]
                        From location
  --to TO [TO ...]      To location
  -s STATION [STATION ...], --station STATION [STATION ...]
                        To location
```

## Installation
```bash
cd <path/to/repo>
pip install . # Installs into site-packages
# or
pip install -e . # Creates a link in site-packages
```