from agent_client import AgentClient

from .container import *

class Node:
    def __init__(self, host):
        self.host = host

    def containers(self):
        client = AgentClient(self.host)
        return client.containers()
