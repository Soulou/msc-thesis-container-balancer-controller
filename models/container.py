from agent_client import AgentClient
import time
import socket
import front
import json

class ContainerJSONEncoder(json.JSONEncoder):
    def default(self, o):
        return o.to_json()

class Container:
    def __init__(self, host, info):
        self.host = host
        self.info = info

    def __str__(self):
        return "<{} - {} - {} - {}>".format(self.host, self.port(), self.service(), self.image())

    def to_json(self):
        self.info['Host'] = self.host
        return self.info

    def port(self):
        try:
            return self.info['Ports'][0]['PublicPort']
        except KeyError:
            port_bindings = self.info["NetworkSettings"]["Ports"]
            for remote_port, bindings in port_bindings.items():
                return bindings[0]["HostPort"]

    def service(self):
        try:
            return self.info['Name'].split("-")[0][1:]
        except KeyError:
            return self.info['Names'][0].split("-")[0][1:]

    def image(self):
        try:
            return self.info['Config']['Image']
        except KeyError:
            return self.info["Image"]

    def migrate(self, node):
        new_container = Container.create(node, self.service(), self.image(), update_routing = False)
        boot_success = False
        for i in range(5):
            try:
                s = socket.create_connection((new_container.host, new_container.port()), timeout=1)
                s.close()
                boot_success = True
                break
            except Exception as e:
                print(e)
                time.sleep(1)

        if not boot_success:
            new_container.delete()
            raise Exception("{} failed to boot".format(new_container))

        front.add_backend(new_container.service(), new_container.host, new_container.port())
        self.delete()
        return new_container

    def delete(self):
        host = self.host
        id = self.info['Id']
        agent = AgentClient(host)
        front.remove_backend(self.service(), host, self.port())
        return agent.stop_container(id)

    def status(self):
        agent = AgentClient(self.host)
        return agent.status_container(self.info['Id'])

    def to_item(self):
        agent = AgentClient(self.host)
        metrics = agent.status_container(self.info['Id'])
        return [metrics["cpu"] / 100, metrics["memory"] // 1000, metrics["net"]["rx"] + metrics["net"]["tx"]]

    @classmethod
    def find(clazz, node, id):
        agent = AgentClient(node.host)
        return Container(node.host, agent.container(id))

    @classmethod
    def create(clazz, node, service, image, update_routing=True):
        agent = AgentClient(node.host) 
        container = Container(node.host, agent.start_container(service, image))

        if update_routing:
            front.add_backend(service, node.host, container.port())
        return container
