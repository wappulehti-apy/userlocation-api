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
        """Get responses to client.

        .. :quickref: Message; Get users responses to client.

        If a response to the clients message exists, it is returned. The returned messages
        are removed and are not returned on subsequent requests.

        :>json List[string] responses: list of *string* responses. Eg. :code:`{'responses': [{'public_id': 'abc123', 'response': 'accepted'}]}`.
        """
        client_id = request.headers.get('clientId')
        app.logger.info('get response "%s" (%s)', client_id, request.remote_addr)

        responses = []

        # save keys for responses to array, fetch responses and delete keys
        # This could be achieved smoother using scan_iter, but fakeredis
        # does not support scan + delete in same loop
        _, keys = app.redis.scan(0, f'response:{client_id}:*', count=10)
        for key in keys:
            responses.append(app.redis.hgetall(key))
            app.redis.delete(key)

        return {'responses': responses}

    def post(self):
        """Send a message from a client to a user.

        .. :quickref: Message; Send a message from a client to a user.

        :reqheader clientId: Unique client ID. Min length 25 characters.
        :<json string public_id: Public ID of user to send message to.
        :<json string message: Message.
        :>json bool success: True if request was succesful.
        """
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
        """Respond to client message.

        .. :quickref: Message; Respond to client message.

        :reqheader Authorization: Basic <myusername>:<mypassword>.
        :param client_id: ID of receiving client.
        :<json string user_id: User ID of responding user.
        :<json string response: Response message.
        :>json bool success: True if request was succesful.
        """
        validate_client_id(client_id)

        args = self.parser.parse_args()
        assert isinstance(args.response, str)

        app.logger.info('response to message from "%s" by "%s" (%s)', client_id, args.user_id, request.remote_addr)

        public_id = RedisMap.get_public_id(args.user_id)

        app.redis.hmset(f'response:{client_id}:{args.user_id}', {'response': args.response, 'public_id': public_id})

        return {'success': True}
