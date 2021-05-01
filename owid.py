"""Our World In Data importer."""
import csv
import datetime
from types import SimpleNamespace
import itertools
from more_itertools import pairwise


def read_country_data(location):
    def stream():
        with open("owid-covid-data.csv", "r") as f:
            yield from [row for row in csv.DictReader(f) if row["location"] == location]

    it = iter(stream())
    first = next(it)
    population = number(first["population"])

    def report(prev, data):
        vaccinations = number(data["people_vaccinated"]) - number(
            prev["people_vaccinated"]
        )
        return SimpleNamespace(
            date=datetime.date.fromisoformat(data["date"]),
            deaths=number(data["new_deaths"]),
            cases=number(data["new_cases"]),
            vaccinations=number(data["new_vaccinations"]),
            vaccinations2=vaccinations
        )

    reports = [
        report(prev, data) for prev, data in pairwise(itertools.chain([first], it))
    ]
    return SimpleNamespace(population=population, reports=reports)


def number(cell: str) -> int:
    return int(float(cell)) if cell else 0


if __name__ == "__main__":
    data = read_country_data("Poland")
    print(f"population: {data.population}")
    for report in data.reports:
        print(report)
