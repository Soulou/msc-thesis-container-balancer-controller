import pyconsul.http
from models import Node

class Consul:
    def __init__(self, host="127.0.0.1", port=8500):
        self.client = pyconsul.http.Consul(host=host, port=port)

    def nodes(self):
        return list(map((lambda peer: Node(peer.split(":")[0])), self.client.status['peers']))

    def agent_port(self, host):
        consul_nodes = self.client.service("agent")
        for consul_node in consul_nodes:
            if consul_node['Node'] == host:
                return consul_node['ServicePort']
