from agent_client import AgentClient
import front
import json

class ContainerJSONEncoder(json.JSONEncoder):
    def default(self, o):
        return o.to_json()

class Container:
    def __init__(self, host, info):
        self.host = host
        self.info = info

    def to_json(self):
        self.info['Host'] = self.host
        return self.info

    def port(self):
        port_bindings = self.info["NetworkSettings"]["Ports"]
        for remote_port, bindings in port_bindings.items():
            return bindings[0]["HostPort"]

    def service(self):
        try:
            return self.info['Name'].split("-")[0][1:]
        except KeyError:
            return self.info['Names'][0].split("-")[0][1:]

    def migrate(self, node):
        new_container = Container.create(node, self.service())
        self.delete()
        return new_container

    def delete(self):
        host = self.host
        id = self.info['Id']
        agent = AgentClient(host)
        front.remove_backend(self.service(), host, self.port())
        return agent.stop_container(id)

    def to_item(self):
        agent = AgentClient(self.host)
        metrics = agent.status_container(self.info['Id'])
        return [metrics["cpu"] / 100, metrics["memory"] // 1000, metrics["net"]["rx"] + metrics["net"]["tx"]]

    @classmethod
    def find(clazz, host, id):
        agent = AgentClient(host)
        return Container(host, agent.container(id))

    @classmethod
    def create(clazz, host, service, image):
        agent = AgentClient(host)       
        container = Container(host, agent.start_container(service, image))

        front.add_backend(service, host, container.port())
        return Container(host, container.info)
