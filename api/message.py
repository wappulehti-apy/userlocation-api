from api.auth import basic_auth
from flask import current_app as app
from flask import request
from flask_restful import Resource, reqparse
from werkzeug.exceptions import HTTPException
from functools import wraps


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
