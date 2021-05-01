#!/usr/bin/env python3
import csv
import datetime
from population import Population
from typing import NamedTuple, Optional
import itertools
import argparse


def read_country_data(location):
    with open("owid-covid-data.csv", "r") as f:
        yield from [row for row in csv.DictReader(f) if row["location"] == location]


def number(cell: str) -> int:
    return int(float(cell)) if cell else 0


class Person(NamedTuple):
    infected: bool = False
    alive: bool = True
    vaccinated: Optional[datetime.date] = None


def protected(person: Person, today: datetime.date) -> bool:
    """Whether someone is protected from the infection."""
    if person.vaccinated is None:
        return False
    return (today - person.vaccinated).days > 14


def simulate_single_day(population, data):
    # print(data)
    date = datetime.date.fromisoformat(data["date"])

    # Kill some infected people.
    population.affect(
        number(data["new_deaths"]),
        lambda person: person.alive and person.infected,
        lambda person: person._replace(alive=False),
    )

    # Infect some people.
    population.affect(
        number(data["new_cases"]),
        lambda person: person.alive
        and not person.infected
        and not protected(person, date),
        lambda person: person._replace(infected=True),
    )

    # Vaccinate.
    population.affect(
        number(data["new_vaccinations"]),
        lambda person: person.alive
        and not person.infected
        and person.vaccinated is None,
        lambda person: person._replace(vaccinated=date),
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--location", default="Poland")
    args = parser.parse_args()

    it = iter(read_country_data(args.location))
    first = next(it)
    population = Population(size=number(first["population"]), people_factory=Person)
    for data in itertools.chain([first], it):
        simulate_single_day(population, data)

        print(
            dict(
                date=datetime.date.fromisoformat(data["date"]),
                cases=population.count(lambda person: person.infected),
                deaths=population.count(lambda person: not person.alive),
                vaccinated=population.count(
                    lambda person: person.vaccinated is not None
                ),
                vaccinated_but_infected=population.count(
                    lambda person: person.vaccinated is not None and person.infected
                ),
                vaccinated_but_died=population.count(
                    lambda person: person.vaccinated is not None and not person.alive
                ),
            )
        )


if __name__ == "__main__":
    main()
