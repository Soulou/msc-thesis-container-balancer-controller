from agent_client import AgentClient

from .container import *

class Node:
    def __init__(self, host):
        self.host = host

    def containers(self):
        client = AgentClient(self.host)
        return list(map(lambda c: Container(self.host, c), client.containers()))

    def status(self):
        client = AgentClient(self.host)
        return client.status()

    # CPU / RAM / net
    def to_bin(self):
        _10_MB = 10 * 1024 * 1024
        client = AgentClient(self.host)
        status = client.status()
        return [len(status["cpus"]), status["memory"], _10_MB]

