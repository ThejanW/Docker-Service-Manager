#!/usr/bin/env python3
import json
from flask import Flask, request, Response, render_template
from flask_socketio import SocketIO, emit
from utils import Utils

async_mode = None

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)
thread = None

SAMPLE_BASIC_POST = {
    "app": {
        "name": "",
        "action": ""
    }
}

SAMPLE_ADVANCED_POST = {
    "app": {
        "name": "",
        "action": ""
    }
}

SAMPLE_BASIC_RESPONSE = {
    "result": "OK",
    "app": {
        "name": "",
        "status": ""
    }
}

utils = Utils()


@app.route("/")
def index():
    """The index page which provide information about other API end points"""
    services = ["app1", "app2", "app3", "app4"]

    return render_template('index_test.html', services=services, async_mode=socketio.async_mode)


#
# @app.route("/api/<service_name>/status", methods=['GET'])
# def service_status(service_name):
#     return utils.check_status(service_name)


@socketio.on('connect', namespace='/test')
def test_connect():
    global thread
    if thread is None:
        thread = socketio.start_background_task(target=background_thread)
    emit('my_response', {'data': 'Connected'})


def background_thread():
    services = ["app1", "app2", "app3", "app4"]
    while True:
        socketio.sleep(10)
        for service in services:
            socketio.emit('my_response',
                          {'data': "{0}: {1}".format(service, utils.check_status(service))},
                          namespace='/test')


# def init():
#     if not utils.search_container():
#         utils.pull_container_from_hub()
#     utils.start_nginx()


@socketio.on('start', namespace='/test')
def start(message):
    service = message['service']
    stopped = utils.stop_containers(service)
    started = utils.start_container(service)
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


@app.route('/api/gui/<mode>', methods=['GET', 'POST'])
def container_utils(mode):
    content = request.get_json(silent=True)
    response = {
        "result": "",
        "app": {
            "name": "",
            "status": ""
        }
    }
    if not utils.search_container():
        utils.pull_container_from_hub()
    if utils.start_nginx():
        if mode == 'basic':
            app_name = content['app']['name']
            app_action = content['app']['action']
            response["app"]["name"] = app_name
            if app_action == 'start':
                stopped = utils.stop_containers(app_name)
                started = utils.start_container(app_name)
                if stopped & started:  # return "OK"
                    response["result"] = "OK"
                    response["app"]["status"] = utils.check_status(app_name)
            elif app_action == "stop":
                stopped = utils.stop_containers(app_name)
                if stopped:  # return "OK"
                    response["result"] = "OK"
                    response["app"]["status"] = utils.check_status(app_name)
            else:  # return "ERROR"
                response["result"] = "ERROR"
            return Response(response=json.dumps(response), status=200, mimetype="application/json")
        elif mode == 'advanced':
            return "advanced"
        else:  # return "NOT SUPPORTED"
            return "NOT SUPPORTED"


@app.route('/test/<service>')
def test(service):
    return str(utils.start_container(service))


if __name__ == '__main__':
    port = "8765"
    print("Serving on port %s" % port)
    socketio.run(app, port=int(port))
