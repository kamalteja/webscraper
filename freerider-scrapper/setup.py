"""setup.py script for freerider scrapper"""
from setuptools import find_packages, setup

setup(
    name="freerider",
    version="1.0",  # Only for egg-info stuff
    packages=find_packages(include=("freerider/*")),
    scripts=["freerider/frider.py"],
    install_requires=["requests_cache", "beautifulsoup4", "requests"],
    description="Freerider",
)
