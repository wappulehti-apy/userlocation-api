from api.auth import basic_auth
from redismap import redis_map
from datetime import datetime, timedelta
from flask import current_app as app
from flask import request
from flask_restful import Resource, reqparse
from werkzeug.exceptions import HTTPException


class LocationError(Exception):
    pass


def validate_location(longitude, latitude):
    pass


class LocationList(Resource):
    FETCH_RADIUS = 25  # km

    parser = reqparse.RequestParser()
    parser.add_argument('longitude', type=float, default=24.0)
    parser.add_argument('latitude', type=float, default=60.0)

    def get(self):
        app.logger.info('location query from %s', request.remote_addr)
        try:
            args = self.parser.parse_args()
            validate_location(args.longitude, args.latitude)

            # Fetch users
            locations = redis_map.get_locations(args.longitude, args.latitude, self.FETCH_RADIUS)
            response = {'users': [redis_map.to_json(l) for l in locations]}

            return response
        except BaseException as err:
            return {'error': True, 'message': str(err)}, 500


class Location(Resource):
    method_decorators = {'post': [basic_auth.required]}

    parser = reqparse.RequestParser()
    parser.add_argument('longitude', type=float, required=True, help='longitude in format "24.123456', default=24.0)
    parser.add_argument('latitude', type=float, required=True, help='latitude in format "60.123456', default=60.0)
    parser.add_argument('nick', type=str, help='user identifier')

    def post(self, user_id):
        app.logger.info('update location "%s" (%s)', user_id, request.remote_addr)

        try:
            args = self.parser.parse_args()
            validate_location(args.longitude, args.latitude)
            redis_map.update_user_location(user_id, args.longitude, args.latitude, args.nick)
        except HTTPException as err:
            return {'error': True, 'message': err.name, 'detail': err.data.get('message')}, err.code
        except BaseException as err:
            app.logger.error(err)
            return {'error': True, 'message': 'unknown error', 'detail': str(err)}, 500

        app.logger.info('location "%s" set to lon==%f, lat=%f', user_id, args.longitude, args.latitude)
        return {'success': True}

    def delete(self, user_id):
        app.logger.info('remove location "%s" (%s)', user_id, request.remote_addr)

        try:
            redis_map.remove_user_location(user_id)
        except HTTPException as err:
            return {'error': True, 'message': err.name, 'detail': err.data.get('message')}, err.code
        except BaseException as err:
            app.logger.error(err)
            return {'error': True, 'message': 'unknown error', 'detail': str(err)}, 500

        return {'success': True}
