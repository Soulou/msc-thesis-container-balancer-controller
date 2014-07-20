import os
from urllib.parse import urlparse
import redis

def redis_client():
    redis_url = "redis://localhost:6379/0"
    try:
        redis_url = os.environ['REDIS_URL']
    except:
        pass
    url = urlparse(redis_url)
    host = url.netloc.split(":")[0]
    db = int(url.path.split("/")[1])
    return redis.StrictRedis(host=host, port=url.port, db=db)

