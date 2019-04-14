import sys
import os
import logging
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_basicauth import BasicAuth
from sqlalchemy.exc import SQLAlchemyError
from flask_basicauth import BasicAuth
from flask_migrate import Migrate

from database import db
from cache import create_cache
from location import LocationError
from models import Location
from botapi import Bot


def create_app():
    app = Flask(__name__)
    app.logger.setLevel(logging.INFO)
    settings_class = os.getenv('APP_SETTINGS', 'config.Config')
    app.config.from_object(settings_class)
    app.logger.info(f'Loaded APP_SETTINGS from {settings_class}')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.logger.info(f'Connecting to DB at {app.config["SQLALCHEMY_DATABASE_URI"]}')
    db.init_app(app)
    basic_auth = BasicAuth(app)
    migrate = Migrate(app, db)

    app.logger.setLevel(logging.DEBUG)

    basic_auth = BasicAuth(app)
    cache = create_cache(app)

    return app, cache, db, migrate, basic_auth


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


def validate_location(longitude, latitude):
    pass


app, cache, db, migrate, basic_auth = create_app()


@app.route('/contactrequest')
def contactrequest():
    if 'phone' not in request.args:
        return jsonify({'error': True, 'message': 'you must specify phone-parameter'}), 400
    phone = request.args.get('phone')

    bot = Bot(app.config['BOT_WEBHOOK_URL'])
    app.logger.info('sending contact request')

    if bot.send_contact_request(phone):
        return jsonify({'success': True})
    else:
        return jsonify({'success': False})


@app.route('/')
def get_locations():
    try:
        locations = Location.query.all()
        response = {'sellers': [l.to_simple_json() for l in locations]}
    except LocationError as err:
        response = {'error': True, 'message': str(err)}
    app.logger.info('location query from %s', request.remote_addr)
    return jsonify(response)


@app.route('/set/<int:id>')
@basic_auth.required
def set_location(id):
    try:
        latitude = float(request.args.get('latitude'))
        longitude = float(request.args.get('longitude'))
        initials = str(request.args.get('initials'))
        validate_location(longitude, latitude)

        location = Location(id, latitude=latitude, longitude=longitude, initials=initials)
        # Perform upsert with merge()
        db.session.merge(location)
        db.session.commit()
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
