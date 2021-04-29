from simulate import Population
from typing import NamedTuple
import math
from math import isclose


class Person(NamedTuple):
    age: int = 1
    alive: bool = True
    female: bool = False


def underaged(person):
    return person.age < 18


def grow_up(person):
    return person._replace(age=18)


def kill(person):
    return person._replace(alive=False)


def test_population():
    population = Population(10, Person)
    assert 10 == len(population)

    # Population can be iterated over and everyone is the same.
    assert 1 == len(set(population))

    assert 10 == len([p.age for p in population if p.age == 1])
    assert 0 == len([p.age for p in population if p.age == 18])

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


def test_that_affect_is_truly_randomized():
    population = Population(1_000_000, Person)

    # Create two equally big subpopulations.
    population.affect(500_000, underaged, grow_up)

    # Only underages have different sex. 🤷
    population.affect(250_000, underaged, lambda person: person._replace(female=True))

    # Go Thanos style.
    population.affect(500_000, lambda _: True, kill)

    # Both subpopulations should be affected equally. See the TODO in the implementation.
    assert isclose(
        250_000,
        population.count(lambda person: underaged(person) and not person.alive),
        rel_tol=0.1,
    )
    assert isclose(
        250_000,
        population.count(lambda person: not underaged(person) and not person.alive),
        rel_tol=0.1,
    )

    assert isclose(
        125_000,
        population.count(lambda person: person.female and not person.alive),
        rel_tol=0.1,
    )
