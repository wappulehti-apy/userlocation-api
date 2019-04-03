from flask import Flask, jsonify
from flask_basicauth import BasicAuth

app = Flask(__name__)
app.config.from_objAect('config.Config')

basic_auth = BasicAuth(app)


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


@app.route('/')
def get_cooridnates():
    response = geojson(0, 0, app.config['GEO_NAME'])
    return jsonify(response)


if __name__ == '__main__':
    app.run()
