#!/usr/bin/env python3
import os
import sys
import json
from flask import Flask, render_template
from flask_socketio import SocketIO
from utils import Utils, AdvancedUtils

try:
    with open(os.path.join(os.path.dirname(__file__), 'dsm-config.json')) as config_file:
        CONFIGS = json.load(config_file)
except FileNotFoundError:
    sys.exit(1)

DSM_PORT = CONFIGS["dsm_port"]

REVERSE_PROXY = CONFIGS["reverse_proxy"]
REVERSE_PROXY_IMAGE_NAME = "{0}:{1}".format(REVERSE_PROXY["name"], REVERSE_PROXY["version"])
REVERSE_PROXY_VOLUMES = REVERSE_PROXY["volumes"]
REVERSE_PROXY_PORTS = REVERSE_PROXY["ports"]

SERVICES = CONFIGS["services"]

BG_GLOBAL_THREAD = None

UTILS = Utils(base_url=CONFIGS["base_url"])
ADVANCED_UTILS = AdvancedUtils(base_url=CONFIGS["base_url"])

APP = Flask(__name__)
SOCKET_IO = SocketIO(APP, async_mode=None, async_handlers=True)


@APP.route("/")
def index():
    return render_template('index.html', services=CONFIGS['services'])


@SOCKET_IO.on('connect', namespace='/general')
def on_connect():
    global BG_GLOBAL_THREAD
    if BG_GLOBAL_THREAD is None:
        BG_GLOBAL_THREAD = SOCKET_IO.start_background_task(target=bg_thread)


def bg_thread():
    while True:
        SOCKET_IO.sleep(2)
        if UTILS.search_container(image_name=REVERSE_PROXY_IMAGE_NAME):
            UTILS.start_reverse_proxy(image_name=REVERSE_PROXY_IMAGE_NAME,
                                      volumes=REVERSE_PROXY_VOLUMES,
                                      ports=REVERSE_PROXY_PORTS)
            SOCKET_IO.emit('log_init_status', {'status': "SUCCESS"}, namespace='/general')
            for service in SERVICES:
                SOCKET_IO.emit('log_run_status',
                               {'service': "{0}".format(service["name"]),
                                'status': "{0}".format(UTILS.check_status(image_name=service["image_name"]))},
                               namespace='/general')
        else:
            SOCKET_IO.emit('log_init_status', {'status': "INITIALIZATION FAILED"}, namespace='/general')


@SOCKET_IO.on('start', namespace='/general')
def start(message):
    image_name = message['image_name']
    virtual_host = message['virtual_host']
    UTILS.stop_containers(image_name=image_name)
    UTILS.start_container(image_name=image_name, virtual_host=virtual_host)


@SOCKET_IO.on('stop', namespace='/general')
def stop(message):
    image_name = message['image_name']
    UTILS.stop_containers(image_name=image_name)


@SOCKET_IO.on('pull', namespace='/general')
def pull(message):
    image_name = message['image_name']
    name = message['name']
    for out in ADVANCED_UTILS.pull_container_from_hub(image_name=image_name):
        SOCKET_IO.sleep(0)
        SOCKET_IO.emit('log_pull_status', {'data': json.dumps(out), 'name': name}, namespace='/pull_logs')


@SOCKET_IO.on('disconnect', namespace='/general')
def on_disconnect():
    UTILS.stop_containers(image_name=REVERSE_PROXY_IMAGE_NAME)
    for service in SERVICES:
        UTILS.stop_containers(image_name=service["image_name"])


if __name__ == '__main__':
    print("Serving on port %s" % DSM_PORT)
    SOCKET_IO.run(APP, host='0.0.0.0', port=int(DSM_PORT))
