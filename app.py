import sys
import os
import logging
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError
from flask_basicauth import BasicAuth
from flask_migrate import Migrate

from database import db
from cache import create_cache
from location import LocationError
from models import Location


def create_app():
    app = Flask(__name__)
    app.config.from_object(os.environ['APP_SETTINGS'])
    app.logger.info(f'Loaded APP_SETTINGS from {os.environ["APP_SETTINGS"]}')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.logger.info(f'Connecting to DB at {app.config["SQLALCHEMY_DATABASE_URI"]}')
    db.init_app(app)
    migrate = Migrate(app, db)

    app.logger.setLevel(logging.DEBUG)

    basic_auth = BasicAuth(app)
    cache = create_cache(app)

    return app, cache, db, migrate


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


app, cache, db, migrate = create_app()
@app.route('/')
def get_locations():
    try:
        locations = Location.query.all()
        response = {'locations': [l.to_simple_json() for l in locations]}
    except LocationError as err:
        response = {'error': True, 'message': str(err)}
    app.logger.info('location query from %s', request.remote_addr)
    return jsonify(response)


@app.route('/add')
def add_location():
    try:
        longitude = float(request.args.get('longitude')),
        latitude = float(request.args.get('latitude'))
        location = Location(1, latitude=10, longitude=50)
        # Perform upsert with merge()
        db.session.merge(location)
        db.session.commit()
        # validate_location(location)
    except SQLAlchemyError as err:
        app.logger.error('sqlalchemy error from %s: %s', request.remote_addr, err)
        error_detail = type(err.__dict__['orig']).__name__
        return jsonify({'error': True, 'message': 'cannot insert to database', 'detail': error_detail}), 500
    except (ValueError, KeyError, TypeError) as err:
        app.logger.error('invalid location set from %s: %s', request.remote_addr, err)
        return jsonify({'error': True, 'message': 'invalid location', 'detail': str(err)}), 400
    except BaseException as err:
        return jsonify({'error': True, 'message': 'unknown error', 'detail': str(err)}), 500

    app.logger.info('location set (%s) to lon==%f, lat=%f', request.remote_addr, location.longitude, location.latitude)
    return jsonify({'success': True})


if __name__ == '__main__':
    app.run()
