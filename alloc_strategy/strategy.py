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
        elif name == "worst-fit":
            return WorstFitAllocationStrategy()
        elif name == "best-worst-fit":
            return BestWorstFitAllocationStrategy()
        elif name == "first-worst-fit":
            return FirstWorstFitAllocationStrategy()
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
        print(list(map(lambda b: str(b), bins)))
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
        return self.first_fit(item, bins, nodes)

    def first_fit(self, item, bins, nodes):
        for index in range(len(bins)):
            if bins[index].has_capacity_for(item):
                return nodes[index]
        raise "Not enough capacity in the cluster"

class BestFitAllocationStrategy(AnyFitAllocationStrategy):
    def select_node(self, nodes, service):
        (item, bins) = self.generate_problem(nodes, service)
        return self.best_fit(item, bins, nodes)

    def best_fit(self, item, bins, nodes):
        best_remaining_capacity = [100, 100, 100]
        best_fit_index = -1
        for index in range(len(bins)):
            if not bins[index].has_capacity_for(item):
                continue
            rem_capacity = bins[index].get_remaining_capacity()
            if rem_capacity[0] < best_remaining_capacity[0]:
                best_remaining_capacity = rem_capacity
                best_fit_index = index
        if best_fit_index == -1:
            raise "Not enough capacity in the cluster"
        return nodes[best_fit_index]

class WorstFitAllocationStrategy(AnyFitAllocationStrategy):
    def select_node(self, nodes, service):
        (item, bins) = self.generate_problem(nodes, service)
        return self.worst_fit(item, bins, nodes)
    def worst_fit(self, item, bins, nodes):
        worst_remaining_capacity = bins[0].get_remaining_capacity()
        worst_fit_index = 0
        for index in range(len(bins)):
            if index == 0:
                continue
            if not bins[index].has_capacity_for(item):
                continue
            rem_capacity = bins[index].get_remaining_capacity()
            if rem_capacity[0] > worst_remaining_capacity[0]:
                worst_remaining_capacity = rem_capacity
                worst_fit_index = index
        if worst_remaining_capacity[0] == 0 and bins[0].get_remaining_capacity[0] < item[0]:
            raise "Not enough capacity in the cluster"
        return nodes[worst_fit_index]

class BestWorstFitAllocationStrategy(AnyFitAllocationStrategy):
    def select_node(self, nodes, service):
        (item, bins) = self.generate_problem(nodes, service)
        if item[0] != 0:
            return BestFitAllocationStrategy().best_fit(item, bins, nodes)
        else:
            return WorstFitAllocationStrategy().worst_fit(item, bins, nodes)

class FirstWorstFitAllocationStrategy(AnyFitAllocationStrategy):
    def select_node(self, nodes, service):
        (item, bins) = self.generate_problem(nodes, service)
        if item[0] != 0:
            return FirstFitAllocationStrategy().first_fit(item, bins, nodes)
        else:
            return WorstFitAllocationStrategy().worst_fit(item, bins, nodes)

AllocationStrategy.register(RandomAllocationStrategy)
AllocationStrategy.register(RoundRobinAllocationStrategy)
AllocationStrategy.register(FirstFitAllocationStrategy)
AllocationStrategy.register(BestFitAllocationStrategy)
AllocationStrategy.register(WorstFitAllocationStrategy)
AllocationStrategy.register(BestWorstFitAllocationStrategy)
AllocationStrategy.register(FirstWorstFitAllocationStrategy)
