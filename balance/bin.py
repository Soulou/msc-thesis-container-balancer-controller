import json

from .problem import Problem

class BinJSONEncoder(json.JSONEncoder):
    def default(self, o):
        return o.to_json()

class Bin:
    def __init__(self, node, capacity):
        self.node = node
        self.capacity = capacity.copy()
        self.remaining_capacity = capacity.copy()
        self.dimensions = len(capacity)

    def __getitem__(self, index):
        return self.capacity[index]

    def __setitem__(self, index, value):
        self.capacity[index] = value

    def __str__(self):
        return "<{} - {} - {}>".format(str(self.node), self.capacity, self.remaining_capacity)

    def to_json(self):
        return { "capacity": self.capacity, "remaining_capacity": self.remaining_capacity }

    def get_remaining_capacity(self, type="online"):
        if type == "online":
            self._update_remaining_capacity()
        return self.remaining_capacity

    def has_capacity_for(self, item, type="online"):
        print(self)
        print(item)
        if type == "online":
            self._update_remaining_capacity()
        for i in range(self.dimensions):
            if item[i] > self.remaining_capacity[i] - self.capacity[i] * Problem.RESERVE:
                return False
        return True

    # For offline bin packing, we remove the used capacity here
    def add_item(self, item):
        for i in range(self.dimensions):
            self.remaining_capacity[i] -= item[i]

    def _update_remaining_capacity(self):
        status = self.node.status()
        cpu = 0
        for core, usage in status["cpus"].items():
            cpu += usage

        net = 0
        for rxtx, value in status["net"]["docker0"].items():
            net += value

        self.remaining_capacity[0] = self.capacity[0] - (cpu / 100)
        self.remaining_capacity[1] = status["free_memory"]
        self.remaining_capacity[2] = self.capacity[2] - net

