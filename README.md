## Requirements

* Python 3

## Installation

```
virtualenv . -p /usr/bin/python3
pip install -r requirements.txt
```

## Execution

```
export BASE_URL=thesis.dev # Change value if you need
./controller.py [--strategy=random]
```

## API

* Get the status of a given node, like the different resources consumption and total

`GET /node/:host/status`

```json
// Code 404 - Agent not found

// Code 200 - OK
// Content-Type: application/json
{
  "cpus": {
    "cpu0": 44,
    "cpu1": 22,
  },
  "free_memory": 12300000,
  "memory": 27440000,
  "network": {
    "eth0": {
      "tx": 98765,
      "rx": 12345
    }
  }
}
```

* Return a list of containers running on a given host

`GET /node/:host/containers`

```json
// Code 404 - Agent not found

// Code 200 - OK
// Content-Type: application/json
[
  {
    "Id": "0123456789abcdef",
    "Image": "soulou/msc-thesis-memory-http-service",
    "Ports": [
      {
        "PublicPort": 49127,
        "PrivatePort": 3000
      }
    ],
    "Names": [ "service1-1-837" ],
    "Created": 1723454345,
    "Status": "Up"
  },
  {
    ...
  }
]
```


* Return the status of all the nodes of the cluster.

`GET /nodes/status`

```json
// Code 200 - OK
// Content-Type: application/json
{
  "192.169.0.1" : {
    "cpus": {
      "cpu0": 44,
      "cpu1": 22,
    },
    "memory": 27440000,
    "network": {
      "eth0": {
        "tx": 98765,
        "rx": 12345
      }
    }
  },
  "192.168.0.2" : ...
}
```


* This endpoint aims at executing an algorithm of load balancing.
  The name of the algorithm has to be given in the strategy parameter
  The containers and the agents nodes resource usage is gathered then normalized,
  then the algorithm is executed.
  As a result of the problem solving, a set of migration is applied to move
  the containers according to the algorithm solution.

```
POST /balance
  Params:
    strategy: "stillwell_current"
```

```json
// Code 200 - OK
{
  "items": [[0.2, 0.3, 0], [...]],
  "bins": [[1.0, 2.0, 1.0], [...]],
  "problem": {
    "algo": "stillwell_current",
    "mapping": [0,0,0,1,2,3,4],
  },
  "migrations": [
    {
      "Service": "service-1",
      "Started": {
        "host": "182.168.0.2",
        "id": "0123456789abcdef"
      },
      "Stopped": {
        "host": "182.168.0.2",
        "id": "0123456789abcdef"
      }
    },
    {
    ...
    }
  ]
}
```


* Return a list of all the containers running on the cluster
  hosted by each alive node.

`GET /containers`

```json
// Code: 200 - OK
// Content-Type: application/json
[
  {
    "Host": "192.168.1.2",
    "Id": "0123456789abcdef",
    "Image": "soulou/msc-thesis-memory-http-service",
    "Ports": [
      {
        "PublicPort": 49127,
        "PrivatePort": 3000
      }
    ],
    "Names": [ "service1-1-837" ],
    "Created": 1723454345,
    "Status": "Up"
  },
  {
    ...
  }
]
```

* Create a new container

`POST /containers`

```
Code: 201 - Container started

Docker JSON representation of a container:
With an additional field: "Host"
See: http://goo.gl/JrR6f6
```

* Stop and delete a container on a given host

`DELETE /container/:host/:container_id`

```
Code: 404 - Host or Container not found
Code: 204 - Container stopped
```

* Migrate a container, to the most available node

`POST /container/:host/:container_id/migrate`

```json
// Code 200 - Container migrated
{
  "Service": "service-1",
  "Started": {
    "host": "182.168.0.2",
    "id": "0123456789abcdef"
  },
  "Stopped": {
    "host": "182.168.0.2",
    "id": "0123456789abcdef"
  }
}
```
