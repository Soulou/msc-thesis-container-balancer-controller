from .redis_client import redis_client

def remove_backend(service, backend_host, backend_port):
    redis = redis_client()
    controller_url = "192.168.0.1.xip.io"
    frontend_key = "frontend:{}.{}".format(service, controller_url)
    backend_value = "http://{}:{}".format(backend_host, backend_port)
    redis.lrem(frontend_key, 1, backend_value)
