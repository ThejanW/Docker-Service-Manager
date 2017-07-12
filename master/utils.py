import docker
import subprocess


# class Utils(object):
#     def stop_containers(self, image_name):
#         result_success = subprocess.check_output(
#             'docker rm $(docker stop $(docker ps -a -q --filter ancestor=' + image_name + ' --format="{{.ID}}"))',
#             shell=True)
#         print(result_success)
#
#     def start_container(self, image_name):
#         result_success = subprocess.check_output(
#             'docker run -d -e VIRTUAL_HOST=' + image_name + '.tika.dl ' + image_name,
#             shell=True)
#         print(result_success)

class Utils(object):
    def __init__(self):
        self.client = docker.from_env()

    def stop_containers(self, image_name):
        app_ids = self.client.containers.list(filters={'ancestor': image_name})
        [app_id.remove(force=True) for app_id in app_ids]

    def start_container(self, image_name):
        self.client.containers.run(image_name, detach=True, environment={'VIRTUAL_HOST': image_name + '.tika.dl'})
