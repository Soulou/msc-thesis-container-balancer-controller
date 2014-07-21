import requests
import json

class AgentClient:
    def __init__(self, host):
        self.host = host
        self.port = 5000

    def start_container(self, service):
        payload = {"service": service.replace("-", "_")}
        r = requests.post("{}/containers".format(self.__base_url()), data=payload)
        return json.loads(r.text)

    def stop_container(self, container_id):
        requests.delete("{}/container/{}".format(self.__base_url(), container_id))

    def status_container(self, container_id):
        r = requests.get("{}/container/{}/status".format(self.__base_url(), container_id))
        return json.loads(r.text)

    def container(self, id):
        r = requests.get("{}/container/{}".format(self.__base_url(), id))
        return json.loads(r.text)

    def containers(self):
        r = requests.get("{}/containers".format(self.__base_url()))
        return json.loads(r.text)

    def status(self):
        r = requests.get("{}/status".format(self.__base_url()))
        return json.loads(r.text)

    def __base_url(self):
        return "http://{}:{}".format(self.host, self.port)
