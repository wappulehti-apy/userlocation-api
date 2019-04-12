import sys
import os
import logging
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_basicauth import BasicAuth
from cache import create_cache
from location import Location, LocationError


def create_app():
    app = Flask(__name__)
    app.config.from_object(os.environ['APP_SETTINGS'])
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db = SQLAlchemy(app)
    app.logger.setLevel(logging.DEBUG)

    basic_auth = BasicAuth(app)
    cache = create_cache(app)

    return app, cache, db


def set_location(cache, location):
    cache.set('location', location, 5 * 60)


def get_location(cache):
    location = cache.get('location')
    if location is None:
        raise LocationError('location not updated')
    return location


def isFloat(f):
    try:
        float(f)
        return True
    except BaseException as err:
        return False


def validate_location(location):
    if location.lat is None:
        raise KeyError("lat is missing")
    if location.long is None:
        raise KeyError("longitude is missing")
    if not isFloat(location.lat) or not isFloat(location.long):
        raise TypeError("coordinates are not floats")
    return True


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


app, cache, db = create_app()
@app.route('/')
def get_cooridnates():
    try:
        location = get_location(cache)
        response = geojson(location, app.config['GEO_NAME'])
    except LocationError as err:
        response = {'error': True, 'message': str(err)}
    app.logger.info('location query from %s', request.remote_addr)
    return jsonify(response)


@app.route('/set')
def set_coordinates():
    try:
        location = Location(
            long=float(request.args.get('longitude')),
            lat=float(request.args.get('lat'))
        )
        validate_location(location)
    except (ValueError, KeyError, TypeError) as err:
        app.logger.error('invalid location set from %s: %s', request.remote_addr, err)
        return jsonify({'error': True, 'message': 'invalid location', 'detail': str(err)}), 400
    except BaseException as err:
        return jsonify({'error': True, 'message': 'unknown error', 'detail': str(err)}), 500

    set_location(cache, location)
    app.logger.info('location set (%s) to long==%f, lat=%f', request.remote_addr, location.long, location.lat)
    return jsonify({'success': True})


if __name__ == '__main__':
    app.run()
