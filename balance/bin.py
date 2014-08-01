import json

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

    def to_json(self):
        return self.capacity

    def get_remaining_capacity(self):
        self._update_remaining_capacity()
        return self.remaining_capacity

    def has_capacity_for(self, item):
        self._update_remaining_capacity()
        for i in range(self.dimensions):
            if item[i] > self.remaining_capacity[i]:
                return False
        return True

    def _update_remaining_capacity(self):
        status = self.node.status()
        cpu = 0
        for core, usage in status["cpus"].items():
            cpu += usage

        net = 0
        for rxtx, value in status["net"]["docker0"].items():
            net += value

        self.remaining_capacity[0] = self.capacity[0] - (cpu / 100)
        self.remaining_capacity[1] = self.capacity[1] - status["free_memory"]
        self.remaining_capacity[2] = self.capacity[2] - net

