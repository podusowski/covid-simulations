import csv
import datetime
from typing import NamedTuple, Optional
from collections import defaultdict
import copy
import random


POPULATION = 37_846_605


def read_covid_cases_data():
    # https://covid.ourworldindata.org/data/owid-covid-data.csv
    with open("owid-covid-data.csv", "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["location"] == "Poland":
                yield row


class Population:
    def __init__(self, size, people_factory):
        self._subpopulations = defaultdict(lambda: 0)
        self._subpopulations[people_factory()] = size

    def __len__(self):
        return sum([size for size in self._subpopulations.values()])

    def __iter__(self):
        for feature, size in self._subpopulations.items():
            for _ in range(size):
                yield copy.copy(feature)

    def affect(self, size, match, transform):
        """Affect (``transform`` in some way) ``size`` people with features matching ``match``."""
        if not size:
            return  # Function would throw otherwise.

        # Loop below modifies the buckets so we save what's important earlier.
        buckets = [
            (kind, size) for kind, size in self._subpopulations.items() if match(kind)
        ]
        maching_people = sum(size for _, size in buckets)
        assert buckets

        def bucket(n):
            for kind, size in buckets:
                n -= size
                if n <= 0:
                    return kind

        for _ in range(size):
            n = random.randrange(0, maching_people)
            old_kind = bucket(n)
            self._subpopulations[old_kind] -= 1
            new_kind = transform(old_kind)
            self._subpopulations[new_kind] += 1

    def count(self, match):
        return sum(size for kind, size in self._subpopulations.items() if match(kind))


class Person(NamedTuple):
    infected: bool = False
    alive: bool = True
    vaccinated: Optional[datetime.date] = None


def number(cell: str) -> int:
    return int(float(cell)) if cell else 0


def protected(person: Person, today: datetime.date) -> bool:
    if person.vaccinated is None:
        return False
    return (today - person.vaccinated).days > 14


def simulate_single_day(population, data):
    # print(data)
    date = datetime.date.fromisoformat(data["date"])

    # Kill some infected people.
    population.debug = True
    population.affect(
        number(data["new_deaths"]),
        lambda person: person.infected,
        lambda person: person._replace(alive=False),
    )
    population.debug = False

    # Infect some people.
    population.affect(
        int(float(data["new_cases"])),
        lambda person: person.alive
        and not person.infected
        and not protected(person, date),
        lambda person: person._replace(infected=True),
    )

    # Vaccinate.
    population.affect(
        number(data["new_vaccinations"]),
        lambda person: person.alive and not person.infected,
        lambda person: person._replace(vaccinated=date),
    )


def main():
    population = Population(size=POPULATION, people_factory=Person)
    for data in read_covid_cases_data():
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
