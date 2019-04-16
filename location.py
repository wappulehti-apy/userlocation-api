import sys
import os
import re
from gevent import sleep
from datetime import datetime, timedelta
from flask import current_app as app
from flask import Blueprint, request, jsonify, session
from sqlalchemy.exc import SQLAlchemyError

from models import Location
from webhook import Webhook
from database import db

location = Blueprint('location', __name__, url_prefix='/location')
from app import basic_auth  # NOQA


class LocationError(Exception):
    pass


def validate_location(longitude, latitude):
    pass


def valid_phone(phone):
    if len(phone) < 6 or len(phone) > 15:
        return False
    # Must contain at least 3 numbers
    if not re.search(r"\d\d\d", phone):
        return False
    return True


@location.route('/requestcall', methods=['POST'])
def requestcall():
    data = request.get_json()
    phone = data.get('phoneNumber')
    webhook = Webhook(app.config['WEBHOOK_URL'])

    app.logger.info('sending contact request')
    if webhook.send_contact_request(user.id, buyer_id, phone):
        return jsonify({'success': True})
    else:
        return jsonify({'success': False})



@location.route('/')
def get_locations():
    try:
        locations = Location.query.all()
        response = {'sellers': [l.to_simple_json() for l in locations]}
    except LocationError as err:
        response = {'error': True, 'message': str(err)}
    app.logger.info('location query from %s', request.remote_addr)
    return jsonify(response)


@location.route('/set/<int:id>')
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
