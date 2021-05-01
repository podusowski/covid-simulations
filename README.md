This COVID-19 simulation tries to asses how many vaccinated people might still
get infected and die before the immunity system fully kicks in.


How does it work
----------------
The basic building block o the simulation is a model of a population.
Individuals in a population have features which can evolve as the summation
runs, and thus creating subpopulations. Randomly picked individuals can be then
_affected_ (one or more of their features can change) in each simulation cycle.


Quick start
-----------
The simulation was tested under Ubuntu 20.04 with Python 3.8.5. It can be
started with:

```
./simulation.py --location Poland
```


Limitations
-----------
There are number of limitations that you should be aware of before interpreting
any of this.

Things that might cause the numbers to be underestimated:

- For the program, a _protected_ (one that cannot be infected) person is
  everyone two weeks after the first dose of the vaccine.

- In many countries, people in the high risk groups were prioritized to take
  the jabs first, making them overrepresented in the vaccinated subpopulation.
  This might paradoxically mean that the vaccinated subpopulation is
  **at first**, more susceptible to severe complication.

- By default, infected people are not vaccinated. This is only partially true
  because there might be people who did catch the infection say a day before
  the vaccination.


Data
----
The data was taken from https://ourworldindata.org/
