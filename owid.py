"""Our World In Data importer."""
import csv
from types import SimpleNamespace
import itertools


def read_country_data(location):
    def stream():
        with open("owid-covid-data.csv", "r") as f:
            yield from [row for row in csv.DictReader(f) if row["location"] == location]

    it = iter(stream())
    first = next(it)
    population = number(first["population"])

    return SimpleNamespace(population=population, reports=itertools.chain([first], it))


def number(cell: str) -> int:
    return int(float(cell)) if cell else 0
