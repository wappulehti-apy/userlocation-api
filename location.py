from datetime import datetime, timedelta
from flask import current_app as app
from flask import Blueprint, request, jsonify, session
from sqlalchemy.exc import SQLAlchemyError

from models import Location, generate_public_id
from redismap import RedisMap
from webhook import Webhook
from database import db

location = Blueprint('location', __name__, url_prefix='/location')
from app import basic_auth  # NOQA


class LocationError(Exception):
    pass


def validate_location(longitude, latitude):
    pass


@location.route('/')
def get_locations():
    app.logger.info('location query from %s', request.remote_addr)
    try:
        # Fetch sellers
        locations = Location.query.all()
        response = {'sellers': [l.to_simple_json() for l in locations]}
        # Fetch requestcall
        buyer_id = request.headers.get('sessionId')
        if buyer_id:
            app.logger.info(f'buyer {buyer_id}')
            requestcall_status = app.redis.hgetall(f'response:{buyer_id}')
            app.logger.info(requestcall_status)
            if requestcall_status:
                app.redis.hdel(f'response:{buyer_id}', 'response', 'seller_id')
                seller_id = requestcall_status['seller_id']
                response = {**response, 'callRequest': {
                    'sellerId': seller_id,
                    'accepted': requestcall_status['response'] == 'accepted'
                }}

    except LocationError as err:
        response = {'error': True, 'message': str(err)}

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
