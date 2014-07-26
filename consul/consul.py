import pyconsul.http
from models import Node

class Consul:
    def __init__(self, host="127.0.0.1", port=8500):
        self.client = pyconsul.http.Consul(host=host, port=port)

    def nodes(self):
        consul_nodes = self.client.service("agent")
        return list(map((lambda node: Node(node["Address"])), consul_nodes))

    def agent_port(self, host):
        consul_nodes = self.client.service("agent")
        for consul_node in consul_nodes:
            if consul_node['Node'] == host:
                return consul_node['ServicePort']
