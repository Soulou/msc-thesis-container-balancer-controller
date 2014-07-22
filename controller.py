#!/usr/bin/env python3

from random import randint
from flask import Flask
from flask import request
from flask import Response
from consul import Consul
from models import Container
from models import ContainerJSONEncoder
from balance import Problem
from balance import ProblemJSONEncoder
from agent_client import ContainerNotFound
import json

app = Flask(__name__)
app.debug = True

@app.route("/status", methods=['GET'])
def app_status():
    consul = Consul()
    nodes = consul.nodes()
    containers = {}
    for node in nodes:
        containers[node.host] = node.containers()
    return Response(json.dumps(containers, cls=ContainerJSONEncoder), status=200)

@app.route("/node/<host>/status", methods=['GET'])
def app_node_status(host):
    consul = Consul()
    nodes = consul.nodes()
    node_hosts = map((lambda n: n.host), Consul().nodes())
    try:
        index = node_hosts.index(host)
    except ValueError:
        return Response("{} is not in the cluster".format(node), status=422)

    return json.dumps(nodes[index].status())

@app.route("/nodes-status", methods=['GET'])
def app_nodes_status():
    consul = Consul()
    nodes = consul.nodes()
    statuses = {}
    for node in nodes:
        statuses[node.host] = node.status()
    return json.dumps(statuses)

@app.route("/node/<host>/containers", methods=['GET'])
def app_node_containers(host):
    nodes = Consul().nodes()
    node_hosts = list(map((lambda n: n.host), Consul().nodes()))
    try:
        index = node_hosts.index(host)
    except ValueError:
        return Response("{} is not in the cluster".format(node), status=422)

    return Response(json.dumps(nodes[index].containers(), cls=ContainerJSONEncoder), status=200)

@app.route("/balance", methods=['POST'])
def app_balance_containers():
    consul = Consul()
    nodes = consul.nodes()
    problem = Problem()
    for node in nodes:
        containers = node.containers()
        for container in containers:
            try:
                problem.items.append(container.to_item())
            except ContainerNotFound:
                pass
        problem.bins.append(node.to_bin())
    problem.normalize()
    result = problem.solve()
    print(problem.items)
    print(problem.bins)
    print(result)
    result['datetime'] = str(result['datetime'])
    return json.dumps(result)
    # return Response(json.dumps(problem, cls=ProblemJSONEncoder), status=200)

@app.route("/containers", methods=['POST'])
def app_new_container():
    try:
        service = request.form['service']
    except KeyError:
        return Response("service field should be provided", status=422)
    consul = Consul()
    nodes = consul.nodes()
    selected_host = nodes[randint(0, len(nodes)-1)].host

    try:
        image = request.form['image']
    except KeyError:
        image = "soulou/msc-thesis-fibo-http-service"

    started_container = Container.create(selected_host, service, image)
    return Response(json.dumps(started_container, cls=ContainerJSONEncoder), status=201)

@app.route("/container/<host>/<container_id>", methods=['DELETE'])
def app_delete_container(host, container_id):
    hosts = list(map((lambda n: n.host), Consul().nodes()))
    try:
        hosts.index(host)
    except ValueError:
        return Response("{} is not in the cluster".format(host), status=422)

    Container.find(host, container_id).delete()
    return Response("", status=204)

@app.route("/container/<host>/<container_id>/migrate", methods=['POST'])
def app_migrate_container(host, container_id):
    nodes = Consul().nodes()
    selected_host = nodes[randint(0, len(nodes)-1)].host

    running_container = Container.find(host, container_id)
    new_container = Container.create(selected_host, running_container.service())
    running_container.delete()
    return Response(json.dumps(
        {"Started": new_container,
         "Stopped": running_container}, cls=ContainerJSONEncoder), status=201)

if __name__ == "__main__":
    app.run(port=5001, host='0.0.0.0')
