#!/usr/bin/env python2

from random import randint
from flask import Flask
from flask import json
from flask import request
from flask import Response
from consul import Consul
from models import Task

app = Flask(__name__)
app.debug = True

@app.route("/status", methods=['GET'])
def app_status():
    consul = Consul()
    nodes = consul.nodes()
    tasks = {}
    for node in nodes:
        tasks[node.host] = node.tasks()
    return json.dumps(tasks)

@app.route("/node/<host>/tasks", methods=['GET'])
def app_node_tasks(host):
    nodes = Consul().nodes()
    node_hosts = map((lambda n: n.host), Consul().nodes())
    try:
        index = node_hosts.index(host)
    except ValueError:
        return Response("{} is not in the cluster".format(node), status=422)

    return json.dumps(nodes[index].tasks())

@app.route("/tasks", methods=['POST'])
def app_new_task():
    consul = Consul()
    nodes = consul.nodes()
    selected_host = nodes[randint(0, len(nodes)-1)].host
    t = Task.create(selected_host)
    return Response(json.dumps({selected_host: t}), status=201)

@app.route("/task/<node>/<task_id>", methods=['DELETE'])
def app_delete_task(node, task_id):
    nodes = map((lambda n: n.host), Consul().nodes())
    try:
        nodes.index(node)
    except ValueError:
        return Response("{} is not in the cluster".format(node), status=422)

    Task.delete(node, task_id)
    return Response("", status=204)


if __name__ == "__main__":
    app.run(port=5001, host='0.0.0.0')
