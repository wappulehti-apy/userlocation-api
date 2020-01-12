from api.auth import basic_auth
from api.limiter import rate_limiter
from redismap import redis_map
from flask import current_app as app
from flask import request, abort
from flask_restful import Resource, reqparse
from werkzeug.exceptions import HTTPException


class LocationError(ValueError):
    pass


def validate_location(longitude, latitude):
    if longitude < -180 or longitude > 180:
        abort(400, description='invalid longitude: Must be between -180 and 180.')
    if latitude < -90 or latitude > 90:
        abort(400, description='invalid latitude: Must be between -90 and 90.')


class LocationList(Resource):
    decorators = [rate_limiter.limit('10/minute')]

    FETCH_RADIUS = 25  # km

    parser = reqparse.RequestParser()
    parser.add_argument('longitude', type=float, default=24.0)
    parser.add_argument('latitude', type=float, default=60.0)

    def get(self):
        """List user locations.

        .. :quickref: User Location; List user locations.

        :query float longitude: (optional) Longitude around which to fetch users.
        :query float latitude: (optional) Latitude around which to fetch users.
        :>json List[object] users: User list
        """
        app.logger.info('location query from %s', request.remote_addr)
        args = self.parser.parse_args()
        validate_location(args.longitude, args.latitude)

        # Fetch users
        locations = redis_map.get_locations(args.longitude, args.latitude, self.FETCH_RADIUS)
        response = {'users': [redis_map.to_json(l) for l in locations]}

        return response


class Location(Resource):
    method_decorators = [basic_auth.required]

    parser = reqparse.RequestParser()
    parser.add_argument('longitude', type=float, required=True, help='longitude in format "24.123456"')
    parser.add_argument('latitude', type=float, required=True, help='latitude in format "60.123456"')
    parser.add_argument('nick', type=str, help='nick for user, eg. "bob"', required=True)

    def post(self, user_id):
        """Add or update user location.

        .. :quickref: User Location; Add or update user location.

        :reqheader Authorization: Basic <myusername>:<mypassword>.
        :param int user_id: User ID.
        :query float longitude: Longitude around which to fetch users.
        :query float latitude: Latitude around which to fetch users.
        :query string nick: Nickname or alias for user.
        :>json bool success: True if request was succesful.
        """
        app.logger.info('update location "%s" (%s)', user_id, request.remote_addr)

        args = self.parser.parse_args()
        validate_location(args.longitude, args.latitude)
        redis_map.update_user_location(user_id, args.longitude, args.latitude, args.nick)

        app.logger.info('location "%s" set to lon==%f, lat=%f', user_id, args.longitude, args.latitude)
        return {'success': True}

    def delete(self, user_id):
        """Remove user and location.

        .. :quickref: User Location; Remove user location.
        .. note:: Locations are also expired automatically after a given period.

        :reqheader Authorization: Basic <myusername>:<mypassword>.
        :param int user_id: User ID.
        :>json bool success: True if request was succesful.
        """
        app.logger.info('remove location "%s" (%s)', user_id, request.remote_addr)

        redis_map.remove_user_location(user_id)

        return {'success': True}
