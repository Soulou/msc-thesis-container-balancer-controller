import requests
import json

class AgentClient:
    def __init__(self, host):
        self.host = host
        self.port = 5000

    def start_task(self):
        r = requests.post("{}/tasks".format(self.__base_url()))
        return json.loads(r.text)

    def stop_task(self, task_id):
        requests.delete("{}/task/{}".format(self.__base_url(), task_id))

    def tasks(self):
        r = requests.get("{}/tasks".format(self.__base_url()))
        return json.loads(r.text)

    def __base_url(self):
        return "http://{}:{}".format(self.host, self.port)
