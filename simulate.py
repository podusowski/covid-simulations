import csv
from typing import NamedTuple
from collections import defaultdict
import copy


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
        def find_kind():
            for kind in self._buckets.keys():
                if match(kind):
                    return kind

        old_kind = find_kind()
        assert self._buckets[old_kind] >= size
        self._buckets[old_kind] -= size
        new_kind = transform(old_kind)
        self._buckets[new_kind] += size


def main():
    for day in read_covid_cases_data():
        print(day["date"])


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

    population.affect(3, underaged, grow_up)
    assert 4 == len([p.age for p in population if p.age == 1])
    assert 6 == len([p.age for p in population if p.age == 18])

    population.affect(4, underaged, grow_up)
    assert 0 == len([p.age for p in population if p.age == 1])
    assert 10 == len([p.age for p in population if p.age == 18])
