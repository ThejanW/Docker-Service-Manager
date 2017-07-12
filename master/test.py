#!/usr/bin/env python
from utils import Utils
import docker

Utils().stop_containers("app1")
# Utils().start_container("app1")

# client = docker.from_env()
# client.containers.run("app1", ports={'8765/tcp': 8765})
