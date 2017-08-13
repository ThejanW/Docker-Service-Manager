#!/usr/bin/env python3
import json
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from utils import Utils, AdvancedUtils

app = Flask(__name__)
app.static_url_path = ''
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=None, async_handlers=True)
thread = None

with open('dsm-config.json') as config_file:
    configs = json.load(config_file)

utils = Utils(base_url=configs["base_url"])
adv_utils = AdvancedUtils(base_url=configs["base_url"])


@app.route("/")
def index():
    """The index page which provide information about other API end points"""

    return render_template('index.html', services=configs['services'])


@socketio.on('connect', namespace='/general')
def on_connect():
    global thread
    if thread is None:
        thread = socketio.start_background_task(target=bg_thread)


def bg_thread():
    reverse_proxy = configs["reverse_proxy"]
    reverse_proxy_image_name = "{0}:{1}".format(reverse_proxy["name"], reverse_proxy["version"])
    reverse_proxy_volumes = reverse_proxy["volumes"]
    reverse_proxy_ports = reverse_proxy["ports"]
    services = configs["services"]
    while True:
        socketio.sleep(2)
        if utils.search_container(image_name=reverse_proxy_image_name):
            utils.start_reverse_proxy(image_name=reverse_proxy_image_name,
                                      volumes=reverse_proxy_volumes,
                                      ports=reverse_proxy_ports)
            socketio.emit('log_init_status', {'status': "SUCCESS"}, namespace='/general')
            for service in services:
                socketio.emit('log_run_status',
                              {'service': "{0}".format(service["name"]),
                               'status': "{0}".format(utils.check_status(image_name=service["image_name"]))},
                              namespace='/general')
        else:
            socketio.emit('log_init_status', {'status': "INITIALIZATION FAILED"}, namespace='/general')


@socketio.on('start', namespace='/general')
def start(message):
    image_name = message['image_name']
    virtual_host = message['virtual_host']
    utils.stop_containers(image_name=image_name)
    utils.start_container(image_name=image_name, virtual_host=virtual_host)


@socketio.on('stop', namespace='/general')
def stop(message):
    image_name = message['image_name']
    utils.stop_containers(image_name=image_name)


@socketio.on('pull', namespace='/general')
def pull(message):
    image_name = message['image_name']
    name = message['name']
    for out in adv_utils.pull_container_from_hub(image_name=image_name):
        socketio.sleep(0)
        print(json.dumps(out))
        socketio.emit('log_pull_status', {'data': json.dumps(out), 'name': name}, namespace='/pull_logs')


if __name__ == '__main__':
    port = configs["dsm_port"]
    print("Serving on port %s" % port)
    socketio.run(app, port=int(port))
