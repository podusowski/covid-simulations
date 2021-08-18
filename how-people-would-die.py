#!/usr/bin/env python3
import datetime

from matplotlib.pyplot import title
from owid import number, read_country_data
from population import Population
from typing import NamedTuple, Optional
import argparse
from pprint import pprint
import sys


class Person(NamedTuple):
    alive: bool = True
    died: Optional[datetime.date] = None
    vaccinated: Optional[datetime.date] = None


def simulate_single_day(args, population: Population, data):
    # Vaccinate.
    population.affect(
        data.vaccinations,
        lambda person: person.alive and person.vaccinated is None,
        lambda person: person._replace(vaccinated=data.date),
    )

    # Kill some people.
    population.affect(
        1000,
        lambda person: person.alive,
        lambda person: person._replace(alive=False, died=data.date),
    )


def plot(args, reports):
    # Import lazy because it takes some time.
    import matplotlib.pyplot as plt

    dates = [report["date"] for report in reports]

    def plot(metric):
        plt.plot([report[metric] for report in reports], label=metric)

    plt.title(" ".join(sys.argv[1:]))

    plt.subplot(211)
    plot("vaccinated_and_died")
    plt.legend()

    plt.subplot(212)
    plot("died_within_a_week_after_vaccination")
    plot("died_within_a_day_after_vaccination")
    plt.legend()

    # plt.subplot(222)
    # plot("deaths")
    # plt.legend()

    # plt.subplot(223)
    # plot("vaccinated_but_infected")
    # plt.legend()

    # plt.subplot(224)
    # plot("vaccinated_but_died")
    # plt.legend()

    plt.savefig(args.plot)


def simulate(args):
    data = read_country_data(args.location)
    population = Population(size=data.population, people_factory=Person)
    print(population.count(lambda _: True))
    for data in data.reports:
        sys.stderr.write(".")
        sys.stderr.flush()
        simulate_single_day(args, population, data)

        def died_after_vaccination(person: Person, within: datetime.timedelta):
            if person.died is None or person.vaccinated is None:
                return  # Died unvaccinated.
            return person.died - person.vaccinated < within

        yield dict(
            date=data.date,
            deaths=population.count(lambda person: not person.alive),
            vaccinated=population.count(lambda person: person.vaccinated is not None),
            vaccinated_and_died=population.count(
                lambda person: person.vaccinated is not None and not person.alive
            ),
            died_within_a_week_after_vaccination=population.count(
                lambda person: died_after_vaccination(
                    person, within=datetime.timedelta(days=7)
                )
            ),
            died_within_a_day_after_vaccination=population.count(
                lambda person: died_after_vaccination(
                    person, within=datetime.timedelta(days=1)
                )
            ),
        )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--location", default="Poland")
    parser.add_argument("--plot", default=None)
    args = parser.parse_args()

    reports = simulate(args)

    if args.plot:
        reports = list(reports)
        pprint(reports[-1])
        plot(args, reports)
    else:
        for report in reports:
            pprint(report)


if __name__ == "__main__":
    main()
