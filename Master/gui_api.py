#!/usr/bin/env python3
import json
from flask import Flask, render_template
from flask_socketio import SocketIO
from utils import Utils, AdvancedUtils

app = Flask(__name__)
socket_io = SocketIO(app, async_mode=None, async_handlers=True)
thread = None

with open('dsm-config.json') as config_file:
    configs = json.load(config_file)

utils = Utils(base_url=configs["base_url"])
adv_utils = AdvancedUtils(base_url=configs["base_url"])


@app.route("/")
def index():
    return render_template('index.html', services=configs['services'])


@socket_io.on('connect', namespace='/general')
def on_connect():
    global thread
    if thread is None:
        thread = socket_io.start_background_task(target=bg_thread)


def bg_thread():
    reverse_proxy = configs["reverse_proxy"]
    reverse_proxy_image_name = "{0}:{1}".format(reverse_proxy["name"], reverse_proxy["version"])
    reverse_proxy_volumes = reverse_proxy["volumes"]
    reverse_proxy_ports = reverse_proxy["ports"]
    services = configs["services"]
    while True:
        socket_io.sleep(2)
        if utils.search_container(image_name=reverse_proxy_image_name):
            utils.start_reverse_proxy(image_name=reverse_proxy_image_name,
                                      volumes=reverse_proxy_volumes,
                                      ports=reverse_proxy_ports)
            socket_io.emit('log_init_status', {'status': "SUCCESS"}, namespace='/general')
            for service in services:
                socket_io.emit('log_run_status',
                               {'service': "{0}".format(service["name"]),
                                'status': "{0}".format(utils.check_status(image_name=service["image_name"]))},
                               namespace='/general')
        else:
            socket_io.emit('log_init_status', {'status': "INITIALIZATION FAILED"}, namespace='/general')


@socket_io.on('start', namespace='/general')
def start(message):
    image_name = message['image_name']
    virtual_host = message['virtual_host']
    utils.stop_containers(image_name=image_name)
    utils.start_container(image_name=image_name, virtual_host=virtual_host)


@socket_io.on('stop', namespace='/general')
def stop(message):
    image_name = message['image_name']
    utils.stop_containers(image_name=image_name)


@socket_io.on('pull', namespace='/general')
def pull(message):
    image_name = message['image_name']
    name = message['name']
    for out in adv_utils.pull_container_from_hub(image_name=image_name):
        socket_io.sleep(0)
        socket_io.emit('log_pull_status', {'data': json.dumps(out), 'name': name}, namespace='/pull_logs')


if __name__ == '__main__':
    port = configs["dsm_port"]
    print("Serving on port %s" % port)
    socket_io.run(app, host='0.0.0.0', port=int(port))
