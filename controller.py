#!/usr/bin/env python3

import argparse
from flask import current_app
from flask import Flask
from flask import request
from flask import Response
from models import Node
from models import Container
from models import ContainerJSONEncoder
from balance import Problem
from balance import ProblemJSONEncoder
from balance import BinJSONEncoder
from agent_client import ContainerNotFound
from alloc_strategy import AllocationStrategy
import json

app = Flask(__name__)
app.debug = True

@app.route("/status", methods=['GET'])
def app_status():
    nodes = Node.all()
    containers = {}
    for node in nodes:
        containers[node.host] = node.containers()
    return Response(json.dumps(containers, cls=ContainerJSONEncoder), status=200)

@app.route("/node/<host>/status", methods=['GET'])
def app_node_status(host):
    try:
        node = Node.find(host)
    except ValueError:
        return Response("{} is not in the cluster".format(node), status=422)

    return json.dumps(node.status())

@app.route("/nodes/status", methods=['GET'])
def app_nodes_status():
    nodes = Node.all()
    statuses = {}
    for node in nodes:
        statuses[node.host] = node.status()
    return json.dumps(statuses)

@app.route("/node/<host>/containers", methods=['GET'])
def app_node_containers(host):
    try:
        node = Node.find(host)
    except ValueError:
        return Response("{} is not in the cluster".format(node), status=422)
    return Response(json.dumps(node.containers(), cls=ContainerJSONEncoder), status=200)

@app.route("/node/<host>/<cid>/status", methods=['GET'])
def app_node_container_status(host, cid):
    try:
        node = Node.find(host)
    except ValueError:
        return Response("{} is not in the cluster".format(node), status=422)
    container = Container.find(node, cid)
    return json.dumps(container.status())


@app.route("/balance", methods=['POST'])
def app_balance_containers():
    strategy = None
    try:
        strategy = request.form["request"]
    except ValueError:
        pass

    nodes = Node.all()
    problem = Problem(strategy)
    containers = []
    for node in nodes:
        containers += node.containers()
        problem.bins.append(node.to_bin())

    for container in containers:
        try:
            problem.items.append(container.to_item())
        except ContainerNotFound:
            pass

    problem.normalize()
    result = problem.solve()
    mapping = result['mapping']
    migrations = []
    for i in range(len(mapping)):
        # If the node didn't change, next elem of the results
        if nodes[mapping[i]].host == containers[i].host:
            continue

        # If it has changed, migrate the container to the giving node
        new_container = containers[i].migrate(nodes[mapping[i]])
        migrations.append({
            "Service": container.service(),
            "Started": { "Node": new_container.host, "Id": new_container.info["Id"]},
            "Stopped": { "Node": containers[i].host, "Id": containers[i].info["Id"]}
        })

    result['datetime'] = str(result['datetime'])
    return json.dumps({"items": problem.items, "bins": problem.bins, "result": result, "migrations": migrations}, cls=BinJSONEncoder)

@app.route("/containers", methods=['POST'])
def app_new_container():
    try:
        service = request.form['service']
    except KeyError:
        return Response("service field should be provided", status=422)
    nodes = Node.all()

    strategy = AllocationStrategy.from_name(current_app.config['strategy'])
    selected_node = strategy.select_node(nodes, service)

    try:
        image = request.form['image']
    except KeyError:
        image = "soulou/msc-thesis-fibo-http-service"

    started_container = Container.create(selected_node, service, image)
    return Response(json.dumps(started_container, cls=ContainerJSONEncoder), status=201)

@app.route("/container/<host>/<cid>", methods=['DELETE'])
def app_delete_container(host, cid):
    try:
        node = Node.find(host)
    except ValueError:
        return Response("{} is not in the cluster".format(host), status=422)

    Container.find(node, cid).delete()
    return Response("", status=204)

@app.route("/container/<host>/<cid>/migrate", methods=['POST'])
def app_migrate_container(host, cid):
    try:
        node = Node.find(host)
    except ValueError:
        return Response("{} is not in the cluster".format(host), status=422)

    container = Container.find(node, cid)

    nodes = Node.all()

    strategy = AllocationStrategy.from_name(current_app.config['strategy'])
    selected_node = strategy.select_node(nodes, container.service())

    new_container = container.migrate(selected_node)
    return Response(json.dumps(
        {"Started": new_container,
         "Stopped": container}, cls=ContainerJSONEncoder), status=201)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Controller of a container balancer infrastructure')
    parser.add_argument('--strategy', dest='strategy', default='random',
        help='Strategy to use for allocating the containers')

    args = parser.parse_args()
    app.config['strategy'] = args.strategy
    print("Start controller with {} allocation strategy".format(args.strategy))
    app.run(port=5001, host='0.0.0.0')
