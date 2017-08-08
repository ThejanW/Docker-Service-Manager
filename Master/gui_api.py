#!/usr/bin/env python3
import json
from flask import Flask, request, Response, render_template
from flask_socketio import SocketIO, emit
from utils import Utils, AdvancedUtils

async_mode = None

app = Flask(__name__)
app.static_url_path = ''
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)
thread = None

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
    services = ["service1", "service2", "service3", "service4"]
    while True:
        socketio.sleep(3)
        for service in services:
            socketio.emit('log_run_status',
                          {'service': "{0}".format(service),
                           'status': "{0}".format(utils.check_status(service))},
                          namespace='/test')


@socketio.on('init', namespace='/build')
def init():
    if not utils.search_container("app5"):
        # for out in adv_utils.pull_container_from_hub('jwilder/nginx-proxy:latest'):
        for out in adv_utils.pull_container_from_hub('puppet/puppetserver'):
            socketio.sleep(0)
            print(out)
            socketio.emit('log_build_status', {'data': str(out)}, namespace='/build')
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


if __name__ == '__main__':
    port = configs["dsm_port"]
    print("Serving on port %s" % port)
    socketio.run(app, port=int(port))
