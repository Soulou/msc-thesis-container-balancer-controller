from abc import ABCMeta,abstractmethod
from random import randint

class AllocationStrategy(metaclass=ABCMeta):
    @classmethod
    def from_name(clazz, name):
        if name == "random":
            return RandomAllocationStrategy()
        elif name == "round-robin":
            return RoundRobinAllocationStrategy()
        else:
            raise "Strategy {} not implemented.".format(name)

    @abstractmethod
    def select_node(self, nodes):
        return

class RandomAllocationStrategy(AllocationStrategy):
    def select_node(self, nodes):
        return nodes[randint(0, len(nodes)-1)]

class RoundRobinAllocationStrategy(AllocationStrategy):
    def select_node(self, nodes):
        if getattr(self, "nodes", None) == None:
            self.nodes = nodes
            self.current_index = 0
        elif len(self.nodes) != len(nodes):
            print("List of nodes changed, reset round-robin")
            self.nodes = nodes
            self.current_index = 0

        node = self.nodes[self.current_index]
        self.current_index += 1
        if self.current_index == len(self.nodes):
            self.current_index = 0
        return node

AllocationStrategy.register(RandomAllocationStrategy)
AllocationStrategy.register(RoundRobinAllocationStrategy)
