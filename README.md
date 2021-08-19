How does it work
----------------
The simulation is written in Python and it was tested under Ubuntu 20.04 with
Python 3.8.5. `requirements.txt` contains a list of dependencies.

The basic building block o the simulation is a model of a population.
Individuals in a population have features which can evolve as the summation
runs, and thus creating subpopulations. Randomly picked individuals can be then
_affected_ (one or more of their features can change) in each simulation cycle.


Data
----
The data about daily cases, deaths and vaccinations was taken from
https://ourworldindata.org/ and added to the repository.

It can be updated with:

```
wget https://covid.ourworldindata.org/data/owid-covid-data.csv
```


How many people we expect to get infected after vaccination?
------------------------------------------------------------
This COVID-19 simulation tries to asses how many vaccinated people might still
get infected and die before the immunity system fully kicks in.

It can be started by:

```
./simulate.py --location Poland --plot plot.png
```

`--plot` can be skipped to see the raw computed data instead.


There are number of known (and probably some unknown) limitations that you
should be aware of. Make sure you understand them before interpreting any of
this.

Things that might cause the numbers to be underestimated:

- For the program, a _protected_ person is everyone two weeks after the first
  dose of the vaccine. In other words, no one can be infected two weeks after
  vaccination, which obviously isn't the case in the real world.

- In many countries, people in the high risk groups were prioritized to take
  jabs first, making them overrepresented in the vaccinated subpopulation.

- By default, infected people are not vaccinated. This is only partially true
  because there might be people who did catch the infection say a day before
  the vaccination. You can change this behavior to vaccinate despite the 
  infection by `--vaccinate-despite-infection`.


Simulation performed with data from the beginning of the pandemic
to 28 April 2021:

![](plots/plot1.png)

This is what happens if we allow infected people to be vaccinated:

![](plots/plot2.png)

