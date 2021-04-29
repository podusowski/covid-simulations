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

        # There might be multiple subpopulations matching the requested features.
        subpopulations = [
            (features, size)
            for features, size in self._subpopulations.items()
            if match(features)
        ]
        subpopulations_size = sum(size for _, size in subpopulations)

        assert subpopulations

        def features(position):
            for features, size in subpopulations:
                position -= size
                if position <= 0:
                    return features

        for _ in range(size):
            # Pick some dude from the all subpopulations as if they were flattened out.
            position = random.randrange(0, subpopulations_size)

            # Find out what subpopulation the dude was in.
            old_features = features(position)

            # And finally move him around.
            self._subpopulations[old_features] -= 1
            new_features = transform(old_features)
            self._subpopulations[new_features] += 1

    def count(self, match):
        return sum(size for kind, size in self._subpopulations.items() if match(kind))


class Person(NamedTuple):
    infected: bool = False
    alive: bool = True
    vaccinated: Optional[datetime.date] = None


def number(cell: str) -> int:
    return int(float(cell)) if cell else 0


def protected(person: Person, today: datetime.date) -> bool:
    """Whether someone is protected from the infection."""
    if person.vaccinated is None:
        return False

    # The two weeks are taken from CDC:
    #
    # https://www.cdc.gov/coronavirus/2019-ncov/vaccines/keythingstoknow.html
    #
    # On one side, this doesn't take into account a partial protection someone might have earlier
    # than that. On the other hand, it assumes that everyone is fully protected after a first dose,
    # which obviously isn't true.
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
