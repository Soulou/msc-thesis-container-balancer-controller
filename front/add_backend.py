from .redis_client import redis_client

def add_backend(service, backend_host, backend_port):
    redis = redis_client()
    controller_url = "192.168.0.1.xip.io"
    frontend_key = "frontend:{}.{}".format(service, controller_url)
    service_frontends = redis.lrange(frontend_key, 0, -1)
    if len(service_frontends) == 0:
        redis.rpush(frontend_key, service)

    backend_value = "http://{}:{}".format(backend_host, backend_port)
    redis.rpush(frontend_key, backend_value)
