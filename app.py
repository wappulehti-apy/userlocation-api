import sys
from flask import Flask, jsonify
from flask_basicauth import BasicAuth
from cache import create_cache
from location import Location, LocationError


def create_app():
    app = Flask(__name__)
    if "pytest" in sys.modules:
        app.config.from_object('config.Testing')
    else:
        app.config.from_object('config.Config')

    basic_auth = BasicAuth(app)
    cache = create_cache(app)

    return app, cache


def set_location(cache, location):
    cache.set('location', location, timeout=5 * 60)


def get_location(cache):
    location = cache.get('location')
    if location is None:
        raise LocationError('location not updated')
    return location


def geojson(location, name):
    return {
        "type": "Feature",
        "geometry": {
            "type": "Point",
            "coordinates": [location.long, location.lat]
        },
        "properties": {
            "name": name
        }
    }


app, cache = create_app()
@app.route('/')
def get_cooridnates():
    try:
        location = get_location(cache)
        response = geojson(location, app.config['GEO_NAME'])
    except LocationError as err:
        response = {'error': True, 'message': str(err)}
    return jsonify(response)


if __name__ == '__main__':
    app.run()
