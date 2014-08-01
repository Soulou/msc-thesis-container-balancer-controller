from abc import ABCMeta,abstractmethod
from consul import Consul
from models import Container
from random import randint

class AllocationStrategy(metaclass=ABCMeta):
    @classmethod
    def from_name(clazz, name):
        if name == "random":
            return RandomAllocationStrategy()
        elif name == "round-robin":
            return RoundRobinAllocationStrategy()
        elif name == "first-fit":
            return FirstFitAllocationStrategy()
        elif name == "best-fit":
            return BestFitAllocationStrategy()
        else:
            raise "Strategy {} not implemented.".format(name)

    @abstractmethod
    def select_node(self, nodes, service):
        return

class RandomAllocationStrategy(AllocationStrategy):
    def select_node(self, nodes, container=None):
        return nodes[randint(0, len(nodes)-1)]

class RoundRobinAllocationStrategy(AllocationStrategy):
    __nodes = None
    __current_index = 0

    def select_node(self, nodes, service):
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


class AnyFitAllocationStrategy(AllocationStrategy):
    def generate_problem(self, nodes, service):
        bins = list(map(lambda n: n.to_bin(), nodes))
        items = self._get_service_metrics(nodes, service)
        if len(items) == 0:
            return [0, 0, 0], bins
        item = self._average_of_items(items)
        print(item)
        print(bins)
        return item, bins

    def _get_service_metrics(self, nodes, service):
        containers = []
        for n in nodes: 
            containers += n.containers_by_service(service)
        containers_items = list(map(lambda c: c.to_item(), containers))
        return containers_items

    def _average_of_items(self, items):
        average_item = []
        for dim in range(len(items[0])):
            sum_dim = 0
            for item in items:
                sum_dim += item[dim]
            average_dim = sum_dim / len(items)
            average_item.append(average_dim)
        return average_item

class FirstFitAllocationStrategy(AnyFitAllocationStrategy):
    def select_node(self, nodes, service):
        (item, bins) = self.generate_problem(nodes, service)
        for index in range(len(bins)):
            if bins[index].has_capacity_for(item):
                return nodes[index]
        raise "Not enough capacity in the cluster"

class BestFitAllocationStrategy(AnyFitAllocationStrategy):
    def select_node(self, nodes, service):
        (item, bins) = self.generate_problem(nodes, service)
        is_first = True
        best_remaining_capacity = []
        best_fit_index = -1
        for index in range(len(bins)):
            if not bins[index].has_capacity_for(item):
                continue
            rem_capacity = bins[index].get_remaining_capacity()
            if is_first:
                best_remaining_capacity = rem_capacity
                best_fit_index = index
                is_first = False
            if rem_capacity[0] > item[0] and rem_capacity[0] < best_remaining_capacity[0]:
                best_remaining_capacity = rem_capacity
                best_fit_index = index
        if best_fit_index == -1:
            raise "Not enough capacity in the cluster"
        return nodes[index]



AllocationStrategy.register(RandomAllocationStrategy)
AllocationStrategy.register(RoundRobinAllocationStrategy)
AllocationStrategy.register(FirstFitAllocationStrategy)
AllocationStrategy.register(BestFitAllocationStrategy)
