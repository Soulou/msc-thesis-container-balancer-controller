import json

from vectorpack import pack_vectors
from .first_fit_decreasing import FirstFitDecreasing
from .best_fit_decreasing import BestFitDecreasing

class InvalidProblem(Exception):
    pass

class ProblemJSONEncoder(json.JSONEncoder):
    def default(self, o):
        return o.to_json()

class Problem:
    RESERVE = 0.2

    def __init__(self, algorithm="stillwell"):
        self.algorithm = algorithm
        self.items = []
        self.bins = []

    def to_json(self):
        return {"items": self.items, "bins": self.bins}

    def validate(self):
        if len(self.items) == 0:
            raise InvalidProblem("no item")
        if len(self.bins) == 0:
            raise InvalidProblem("no bin")

        self.dimensions = len(self.items[0])
        for i in self.items:
            if len(i) != self.dimensions:
                raise InvalidProblem("all items don't have {} dimensions".format(self.dimensions))
        for b in self.bins:
            if b.dimensions != self.dimensions:
                raise InvalidProblem("all bins don't have{} dimensions".format(self.dimensions))

    def solve(self):
        if self.algorithm == "stillwell":
            # In the internal algorithms the reserve is automatically managed
            # In external libs, it's important to remove it from bins before packing
            self.bins_remove_reserve()
            return pack_vectors(self._to_algo_problem(), family='stillwell_current', 
                       pack='pack_by_items', select='none', itemsort='none', binsort='none')
        elif self.algorithm == "brandao2013mvp":
            self.bins_remove_reserve()
            return pack_vectors(problem=self._to_algo_problem(), family='brandao2013mvp')
        elif self.algorithm == "gabay2013vsv":
            self.bins_remove_reserve()
            return pack_vectors(self._to_algo_problem(), family='gabay2013vsv')
        elif self.algorithm == "first-fit-decreasing":
            return FirstFitDecreasing.pack(self.items, self.bins)
        elif self.algorithm == "best-fit-decreasing":
            return BestFitDecreasing.pack(self.items, self.bins)


    def bins_remove_reserve(self):
        for b in self.bins:
            for d in range(self.dimensions):
                b[d] = b[d] * (1 - Problem.RESERVE)

    def normalize(self):
        self.validate()

        for d in range(self.dimensions):
            max_dim = self._get_bin_max_dimension(d)
            for i in self.items:
                i[d] = round(i[d] / max_dim, 4)
            for b in self.bins:
                b[d] = round(b[d] / max_dim, 4)
                b.remaining_capacity[d] = round(b.remaining_capacity[d] / max_dim, 4)

    def _get_bin_max_dimension(self, dim):
        m = self.items[0][dim]
        for b in self.bins:
            if b[dim] > m:
                m = b[dim]
        return m

    def _to_algo_problem(self):
        return { "items": self.items, "bins": self.bins }
