import re
from api.auth import basic_auth
from api.limiter import rate_limiter
from flask import current_app as app
from flask import request, abort
from flask_restful import Resource, reqparse
from werkzeug.exceptions import HTTPException
from functools import wraps
from webhook import webhook
from flask import current_app as app
from redismap import RedisMap, redis_map


def validate_client_id(f):
    """Decorator that ensures headers contain clientId."""
    @wraps(f)
    def wrapped(*args, **kwargs):
        client_id = request.headers.get('clientId')
        if client_id is None:
            return {'error': True, 'message': 'specify clientId in headers'}, 401
        elif len(client_id) < 25:
            return {'error': True, 'message': 'clientId must be at least 25 characters long'}, 400
        return f(*args, **kwargs)

    return wrapped


def valid_phone_number(phone):
    if len(phone) < 6 or len(phone) > 15:
        return False
    # Must contain at least 5 numbers
    if not re.search(r"\d\d.*\d\d\d", phone):
        return False
    # Should only contain these characters
    if re.search(r"[^ 0-9\+\-\(\)]", phone):
        return False
    return True


def validate_args(args):
    """Validate client message. We expect message to be a plain phone number."""
    if not valid_phone_number(args.message):
        abort(400, description='invalid message: must be a valid phone number of format "(+)123 456789')
    if len(args.public_id) < 5:
        abort(400, description='invalid public_id')


class Message(Resource):
    decorators = [rate_limiter.limit('10/minute')]
    method_decorators = [validate_client_id]

    parser = reqparse.RequestParser()
    parser.add_argument('public_id', type=str, required=True)
    parser.add_argument('message', type=str, required=True)

    def get(self):
        client_id = request.headers.get('clientId')
        app.logger.info(f'get response "%s" (%s)', client_id, request.remote_addr)

        response = app.redis.hgetall(f'response:{client_id}')
        if response is None:
            return {'response': []}

        app.redis.delete(f'response:{client_id}')

        return {'response': response}

    def post(self):
        client_id = request.headers.get('clientId')
        validate_client_id(client_id)

        args = self.parser.parse_args()
        validate_args(args)

        app.logger.info('send message from "%s" to "%s" (%s)', client_id, args.public_id, request.remote_addr)

        user_id = redis_map.get_user_id(args.public_id)

        if not webhook.send(client_id=client_id, user_id=user_id, message=args.message):
            app.logger.error('message webhook failed')
            return {'success': False, 'error': True}, 500
        return {'success': True}


class Response(Resource):
    method_decorators = [basic_auth.required]

    parser = reqparse.RequestParser()
    parser.add_argument('user_id', type=int, required=True)
    parser.add_argument('response', type=str, required=True)

    def post(self, client_id):
        validate_client_id(client_id)

        args = self.parser.parse_args()
        assert isinstance(args.response, str)

        app.logger.info('response to message from "%s" by "%s" (%s)', client_id, args.user_id, request.remote_addr)

        public_id = RedisMap.get_public_id(args.user_id)

        app.redis.hmset(f'response:{client_id}', {'response': args.response, 'public_id': public_id})

        return {'success': True}
