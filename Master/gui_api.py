#!/usr/bin/env python3
import json
from flask import Flask, request, Response, render_template
from flask_socketio import SocketIO, emit
from utils import Utils, AdvancedUtils

async_mode = "eventlet"

app = Flask(__name__)
app.static_url_path = ''
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode, async_handlers=True)
thread = None
thread1 = None

with open('dsm-config.json') as config_file:
    configs = json.load(config_file)

utils = Utils(base_url=configs["base_url"])
adv_utils = AdvancedUtils(base_url=configs["base_url"])


@app.route("/")
def index():
    """The index page which provide information about other API end points"""

    return render_template('index.html', services=configs['services'])


@socketio.on('connect', namespace='/test')
def on_connect():
    global thread
    if thread is None:
        thread = socketio.start_background_task(target=background_thread)
    emit('log_run_status', {'data': 'Connected'})


def background_thread():
    services = configs["services"]
    while True:
        socketio.sleep(3)
        for service in services:
            socketio.emit('log_run_status',
                          {'service': "{0}".format(service["name"]),
                           'status': "{0}".format(utils.check_status(service["image_name"]))},
                          namespace='/test')


@socketio.on('init', namespace='/test')
def on_init():
    global thread1
    if thread1 is None:
        thread1 = socketio.start_background_task(target=init)


def init():
    reverse_proxy = configs["reverse_proxy"]
    reverse_proxy_image_name = "{0}:{1}".format(reverse_proxy["name"], reverse_proxy["version"])
    if not utils.search_container(reverse_proxy_image_name):
        for out in adv_utils.pull_container_from_hub(reverse_proxy_image_name):
            socketio.sleep(2)
            print(out)
            socketio.emit('log_build_status', {'data': str(out)}, namespace='/test')
            if out == 'False':
                emit('log_build_status', {'data': 'Couldn\'t Pull Image, Try Again Later'})
    if utils.start_nginx():
        emit('log_build_status', {'data': 'Initialized'})
    else:
        emit('log_build_status', {'data': 'Couldn\'t Initialize'})


@socketio.on('start', namespace='/test')
def start(message):
    service = message['service']
    virtual_host = message['virtual_host']
    stopped = utils.stop_containers(service)
    started = utils.start_container(image_name=service, virtual_host=virtual_host)
    if stopped & started:
        emit('my_response',
             {'data': 'just started {0}'.format(service)})


@socketio.on('stop', namespace='/test')
def stop(message):
    service = message['service']
    stopped = utils.stop_containers(service)
    if stopped:
        emit('my_response',
             {'data': 'just stopped {0}'.format(service)})


@socketio.on('pull', namespace='/test')
def pull(message):
    service = message['service']
    for out in adv_utils.pull_container_from_hub(service):
        socketio.sleep(0)
        print(out)
        socketio.emit('log_build_status', {'data': str(out)}, namespace='/build')
        if out == 'False':
            emit('log_build_status', {'data': 'Couldn\'t Pull Image, Try Again Later'}, namespace='/build')


if __name__ == '__main__':
    port = configs["dsm_port"]
    print("Serving on port %s" % port)
    socketio.run(app, port=int(port))
