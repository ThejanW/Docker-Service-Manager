#!/usr/bin/env python
import flask

app = flask.Flask(__name__)


@app.route("/")
def index():
    """The index page which provide information about other API end points"""

    return "This is service 2"


if __name__ == '__main__':
    port = "8764"
    print("Serving on port %s" % port)
    app.run(host='0.0.0.0', port=port)
