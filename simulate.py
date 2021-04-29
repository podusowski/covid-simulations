import csv
from typing import NamedTuple, Optional
from collections import defaultdict
import copy
from datetime import date


POPULATION = 37846605


def read_covid_cases_data():
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

        def find_kind():
            for kind in self._buckets.keys():
                if match(kind):
                    return kind
            raise RuntimeError(f"{match} did not match anything")

        old_kind = find_kind()
        assert self._buckets[old_kind] >= size
        self._buckets[old_kind] -= size
        new_kind = transform(old_kind)
        self._buckets[new_kind] += size

    def count(self, match):
        return sum([size for kind, size in self._buckets.items() if match(kind)])


class Person(NamedTuple):
    infected: bool = False
    alive: bool = True
    vaccinated: Optional[date] = None


def number(cell: str) -> int:
    return int(float(cell)) if cell else 0


def simulate_single_day(population, data):
    #print(data)
    # Kill some infected people.
    population.affect(
        number(data["new_deaths"]),
        lambda person: person.infected,
        lambda person: person._replace(alive=False),
    )

    # Infect some people.
    population.affect(
        int(float(data["new_cases"])),
        lambda person: not person.infected,
        lambda person: person._replace(infected=True),
    )


def main():
    population = Population(size=POPULATION, people_factory=Person)
    for day in read_covid_cases_data():
        simulate_single_day(population, day)

        # Show the stats.
        cases = population.count(lambda person: person.infected)
        deaths = population.count(lambda person: not person.alive)
        vaccinated = population.count(lambda person: person.vaccinated is not None)

        print(day["date"], cases, deaths, vaccinated)


if __name__ == "__main__":
    main()


def test_population():
    class Person(NamedTuple):
        age: int = 1

    population = Population(10, Person)
    assert 10 == len(population)

    # Population can be iterated over and everyone is the same.
    assert 1 == len(set(population))

    assert 10 == len([p.age for p in population if p.age == 1])
    assert 0 == len([p.age for p in population if p.age == 18])

    def underaged(person):
        return person.age < 18

    def grow_up(person):
        return Person(age=18)

    # Can change someone.
    population.affect(3, underaged, grow_up)
    assert 7 == len([p.age for p in population if p.age == 1])
    assert 3 == len([p.age for p in population if p.age == 18])
    assert 7 == population.count(underaged)

    population.affect(3, underaged, grow_up)
    assert 4 == len([p.age for p in population if p.age == 1])
    assert 6 == len([p.age for p in population if p.age == 18])
    assert 4 == population.count(underaged)

    population.affect(4, underaged, grow_up)
    assert 0 == len([p.age for p in population if p.age == 1])
    assert 10 == len([p.age for p in population if p.age == 18])
    assert 0 == population.count(underaged)
