from collections import defaultdict
import copy
import random


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
