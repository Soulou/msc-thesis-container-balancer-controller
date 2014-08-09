import json

from vectorpack import pack_vectors

class InvalidProblem(Exception):
    pass

class ProblemJSONEncoder(json.JSONEncoder):
    def default(self, o):
        return o.to_json()

class Problem:
    RESERVE = 0.2

    def __init__(self):
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
        return pack_vectors(self._to_algo_problem(), family='stillwell_current', 
                   pack='pack_by_items', select='none', itemsort='none', binsort='none')

    def normalize(self):
        self.validate()

        for d in range(self.dimensions):
            max_dim = self._get_bin_max_dimension(d)
            for i in self.items:
                i[d] = round(i[d] / max_dim, 4)
            for b in self.bins:
                b[d] = round(b[d] / max_dim * (1 - Problem.RESERVE), 4)

    def _get_bin_max_dimension(self, dim):
        m = self.items[0][dim]
        for b in self.bins:
            if b[dim] > m:
                m = b[dim]
        return m

    def _to_algo_problem(self):
        return { "items": self.items, "bins": self.bins }
