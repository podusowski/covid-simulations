import csv
import datetime
from types import SimpleNamespace
from typing import NamedTuple, Optional
from collections import defaultdict
import copy


POPULATION = 37846605


def read_covid_cases_data():
    # https://covid.ourworldindata.org/data/owid-covid-data.csv
    with open("owid-covid-data.csv", "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["location"] == "Poland":
                yield row


class Population:
    def __init__(self, size, people_factory):
        self._buckets = defaultdict(lambda: 0)
        self._buckets[people_factory()] = size

    def __len__(self):
        return sum([size for size in self._buckets.values()])

    def __iter__(self):
        for kind, size in self._buckets.items():
            for _ in range(size):
                yield copy.copy(kind)

    def affect(self, size, match, transform):
        if not size:
            return  # Function would throw otherwise.

        # Loop below modifies the buckets so we save what's important earlier.
        buckets = [(kind, size) for kind, size in self._buckets.items() if match(kind)]
        maching_people = sum(size for _, size in buckets)
        assert buckets

        for old_kind, bucket_size in buckets:
            # TODO: Probably should account for non-zero remainder.
            share = bucket_size / maching_people
            amount = int(share * size)
            assert self._buckets[old_kind] >= amount
            self._buckets[old_kind] -= amount
            new_kind = transform(old_kind)
            self._buckets[new_kind] += amount

    def count(self, match):
        return sum([size for kind, size in self._buckets.items() if match(kind)])


class Person(NamedTuple):
    infected: bool = False
    alive: bool = True
    vaccinated: Optional[datetime.date] = None


def number(cell: str) -> int:
    return int(float(cell)) if cell else 0


def protected(person: Person, today: datetime.date) -> bool:
    # return person.va
    return False


def simulate_single_day(population, data):
    # print(data)
    date = datetime.date.fromisoformat(data["date"])

    # Kill some infected people.
    population.affect(
        number(data["new_deaths"]),
        lambda person: person.infected,
        lambda person: person._replace(alive=False),
    )

    # Infect some people.
    population.affect(
        int(float(data["new_cases"])),
        lambda person: not person.infected and not protected(person, date),
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
    for day in read_covid_cases_data():
        simulate_single_day(population, day)

        print(
            dict(
                date=datetime.date.fromisoformat(day["date"]),
                cases=population.count(lambda person: person.infected),
                deaths=population.count(lambda person: not person.alive),
                vaccinated=population.count(
                    lambda person: person.vaccinated is not None
                ),
                vaccinated_but_infected=population.count(
                    lambda person: person.vaccinated is not None and person.infected
                ),
            )
        )


if __name__ == "__main__":
    main()
