#!/usr/bin/env python3
from utils import Utils
from flask import Flask, request, Response
import json

app = Flask(__name__)

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

    return "I am master"


@app.route('/api/master/<mode>', methods=['GET', 'POST'])
def container_utils(mode):
    content = request.get_json(silent=True)
    response = {
        "result": "",
        "app": {
            "name": "",
            "status": ""
        }
    }
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


if __name__ == '__main__':
    port = "8764"
    print("Serving on port %s" % port)
    app.run(host='0.0.0.0', port=port)
