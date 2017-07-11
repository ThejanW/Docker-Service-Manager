#!/usr/bin/env python
import docker
from utils import Utils
from flask import Flask, request, jsonify

app = Flask(__name__)

SAMPLE_BASIC_POST = {
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


@app.route("/")
def index():
    """The index page which provide information about other API end points"""

    return "I am master"


@app.route('/api/master/<mode>', methods=['GET', 'POST'])
def add_message(mode):
    content = request.get_json(silent=True)
    if mode == "basic":
        app_name = content["app"]["name"]
        app_action = content["app"]["action"]
        if app_action == "start":
            response = Utils().start_container(app_name, "8081", "8881")
            return response


if __name__ == '__main__':
    port = "8500"
    print("Serving on port %s" % port)
    app.run(host='0.0.0.0', port=port)
