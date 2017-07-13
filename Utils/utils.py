#!/usr/bin/env python3
import docker
from docker import errors


class Utils(object):
    def __init__(self):
        self.client = docker.from_env()

    def stop_containers(self, image_name):
        try:
            container_ids = self.client.containers.list(filters={'ancestor': image_name})
            [container_id.remove(force=True) for container_id in container_ids]
            return True
        except docker.errors.APIError:
            return False

    def start_container(self, image_name):
        try:
            self.client.containers.run(image_name, detach=True, environment={'VIRTUAL_HOST': image_name + '.tika.dl'})
            return True
        except (docker.errors.ContainerError, docker.errors.ImageNotFound, docker.errors.APIError):
            return False

    def check_status(self, image_name):
        container_ids = self.client.containers.list(filters={'ancestor': image_name})
        # when stopped and started there should be only one container in the container_ids list
        if len(container_ids) == 0:
            return "STOPPED"
        else:
            if container_ids[0].status == 'running':
                return "RUNNING"
            else:
                return "NOT RUNNING, NOT STOPPED"

    def search_container(self, image_name):
        try:
            self.client.images.get(image_name)
            return True
        except docker.errors.ImageNotFound:
            return False

    def start_nginx(self, image_name='jwilder/nginx-proxy'):
        try:
            if self.check_status(image_name) != "RUNNING":
                self.client.containers.run(image_name, detach=True,
                                           volumes={'/var/run/docker.sock': {'bind': '/tmp/docker.sock', 'mode': 'ro'}},
                                           ports={'80/tcp': 8764})
            return True
        except (docker.errors.ContainerError, docker.errors.ImageNotFound, docker.errors.APIError):
            return False
