from datetime import datetime, timedelta
from flask import current_app as app
from flask import Blueprint, request, jsonify, session
from sqlalchemy.exc import SQLAlchemyError

from models import Location, generate_public_id
from redismap import RedisMap
from webhook import Webhook
from database import db

location = Blueprint('location', __name__, url_prefix='/location')
from app import basic_auth, redis_map  # NOQA


class LocationError(Exception):
    pass


def validate_location(longitude, latitude):
    pass


@location.route('/')
def get_locations():
    app.logger.info('location query from %s', request.remote_addr)
    try:
        # Fetch sellers
        locations = redis_map.get_locations(24.0, 60.0, 1000)
        response = {'sellers': [redis_map.to_json(l) for l in locations]}
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

        redis_map.update_user_location(id, longitude, latitude, initials)
        # TODO exception handling

    except BaseException as err:
        return jsonify({'error': True, 'message': 'unknown error', 'detail': str(err)}), 500

    app.logger.info('location set (%s) to lon==%f, lat=%f', request.remote_addr, longitude, latitude)
    return jsonify({'success': True})
