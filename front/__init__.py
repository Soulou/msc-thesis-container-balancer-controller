from .add_backend import *
from .remove_backend import *
from .redis_client import *
import os

try:
    os.environ["BASE_URL"]
except KeyError:
    os.environ["BASE_URL"] = "192.168.0.1.xip.io"
