import re
from gevent import sleep
import uuid
from datetime import datetime, timedelta
from flask import current_app as app
from flask import Blueprint, request, jsonify, session

from models import Location, generate_public_id
from webhook import Webhook

requestcall = Blueprint('requestcall', __name__, url_prefix='/requestcall')
from app import basic_auth, redis_map  # NOQA


def valid_phone(phone):
    if len(phone) < 6 or len(phone) > 15:
        return False
    # Must contain at least 3 numbers
    if not re.search(r"\d\d\d", phone):
        return False
    return True


@requestcall.route('/respond', methods=['POST'])
@basic_auth.required
def post_respond():
    data = request.get_json()
    buyer_id = data.get('buyerId')
    response = data.get('response')
    try:
        user_id = int(data.get('userId'))
    except TypeError:
        return jsonify({'error': True, 'message': 'userId is not numeric'}), 400

    if response not in ['accepted', 'declined']:
        app.logger.info(f'unknown response: {response}')
        return jsonify({'error': True, 'message': 'unknown response'}), 400
    if user_id is None:
        app.logger.info(f'user_id missing')
        return jsonify({'error': True, 'message': 'user_id missing'}), 400

    seller_id = generate_public_id(user_id)
    requestcall_response = {'response': response, 'seller_id': seller_id}
    app.logger.info(f'response for buyer {buyer_id}: {response}')
    app.redis.hmset(f'response:{buyer_id}', requestcall_response)
    # TODO timed out
    return '', 200


@requestcall.route('/', methods=['POST'])
def post_requestcall():
    data = request.get_json()
    phone = data.get('phoneNumber')
    public_id = data.get('sellerId')
    buyer_id = request.headers.get('sessionId')
    user_id = redis_map.user_id(public_id)

    if phone is None or public_id is None:
        return jsonify({'error': True, 'message': 'you must specify phoneNumber and sellerId'}), 400
    if not valid_phone(phone):
        return jsonify({'error': True, 'message': 'phoneNumber is not valid'}), 400
    if not user_id:
        return jsonify({'error': True, 'message': 'no user found'}), 404

    webhook = Webhook(app.config['WEBHOOK_URL'])

    app.logger.info(f'sending requestcall for buyer {buyer_id}')
    if not webhook.send_contact_request(user_id, buyer_id, phone):
        app.logger.info('requestcall failed')
        return jsonify({'success': False, 'error': True}), 500
    return jsonify({'success': True})
