from simulate import Population
from typing import NamedTuple


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
