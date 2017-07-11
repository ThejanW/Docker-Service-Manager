import docker


class Utils(object):
    def __init__(self):
        self.client = docker.from_env()

    def stop_containers(self, image_name):
        app_ids = self.client.containers.list(filters={'ancestor': image_name})
        print([app_id.remove(force=True) for app_id in app_ids])

    def start_container(self, image_name, container_port, host_port):
        print(self.client.containers.run(image_name, ports={container_port + '/tcp': host_port}))
