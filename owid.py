"""Our World In Data importer."""
import csv
import datetime
from types import SimpleNamespace
import itertools


def read_country_data(location):
    def stream():
        with open("owid-covid-data.csv", "r") as f:
            yield from [row for row in csv.DictReader(f) if row["location"] == location]

    it = iter(stream())
    first = next(it)
    population = number(first["population"])

    def report(data):
        return SimpleNamespace(
            date=datetime.date.fromisoformat(data["date"]),
            deaths=number(data["new_deaths"]),
            cases=number(data["new_cases"]),
            vaccinations=number(data["new_vaccinations"])
        )

    reports = [report(data) for data in itertools.chain([first], it)]
    return SimpleNamespace(population=population, reports=reports)


def number(cell: str) -> int:
    return int(float(cell)) if cell else 0
