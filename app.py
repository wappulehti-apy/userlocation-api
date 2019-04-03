import os
import sys
from flask import Flask, jsonify
from flask_basicauth import BasicAuth


def create_app():
    app = Flask(__name__)
    if "pytest" in sys.modules:
        app.config.from_object('config.Testing')
    else:
        app.config.from_object('config.Config')

    basic_auth = BasicAuth(app)

    return app


def geojson(latitude, longitude, name):
    return {
        "type": "Feature",
        "geometry": {
            "type": "Point",
            "coordinates": [latitude, longitude]
        },
        "properties": {
            "name": name
        }
    }


app = create_app()
@app.route('/')
def get_cooridnates():
    response = geojson(0, 0, app.config['GEO_NAME'])
    return jsonify(response)


if __name__ == '__main__':
    app.run()
