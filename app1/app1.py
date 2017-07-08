from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import flask

port = "8764"

app = flask.Flask(__name__)


@app.route("/")
def index():
    """The index page which provide information about other API end points"""

    return "I am app 1"


if __name__ == '__main__':
    print("Serving on port %s" % port)
    app.run(host='0.0.0.0', port=port)
