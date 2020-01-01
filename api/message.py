import re
from api.auth import basic_auth
from flask import current_app as app
from flask import request, abort
from flask_restful import Resource, reqparse
from werkzeug.exceptions import HTTPException
from functools import wraps
from webhook import webhook
from flask import current_app as app


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
    if len(args.user_id) < 5:
        abort(400, description='invalid user_id')


class Message(Resource):
    method_decorators = [validate_client_id]
    parser = reqparse.RequestParser()
    parser.add_argument('user_id', type=str, required=True)
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

        app.logger.info('send message from "%s" to "%s" (%s)', client_id, args.user_id, request.remote_addr)

        if not webhook.send(client_id=client_id, user_id=args.user_id, message=args.message):
            app.logger.error('message webhook failed')
            return {'success': False, 'error': True}, 500
        return {'success': True}
