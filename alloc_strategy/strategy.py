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
    __nodes = None
    __current_index = 0

    def select_node(self, nodes):
        if RoundRobinAllocationStrategy.__nodes == None:
            RoundRobinAllocationStrategy.__nodes = nodes
            RoundRobinAllocationStrategy.__current_index = 0
        elif len(RoundRobinAllocationStrategy.__nodes) != len(nodes):
            print("List of nodes changed, reset round-robin")
            RoundRobinAllocationStrategy.__nodes = nodes
            RoundRobinAllocationStrategy.__current_index = 0

        node = RoundRobinAllocationStrategy.__nodes[RoundRobinAllocationStrategy.__current_index]
        RoundRobinAllocationStrategy.__current_index += 1
        if RoundRobinAllocationStrategy.__current_index == len(RoundRobinAllocationStrategy.__nodes):
            RoundRobinAllocationStrategy.__current_index = 0
        return node

AllocationStrategy.register(RandomAllocationStrategy)
AllocationStrategy.register(RoundRobinAllocationStrategy)
