from agent_client import AgentClient

from .task import *

class Node:
    def __init__(self, host):
        self.host = host

    def tasks(self):
        client = AgentClient(self.host)
        return client.tasks()
