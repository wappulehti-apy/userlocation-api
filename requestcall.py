import re
from gevent import sleep
import uuid
from datetime import datetime, timedelta
from flask import current_app as app
from flask import Blueprint, request, jsonify, session

from models import Location
from webhook import Webhook
from database import db

requestcall = Blueprint('requestcall', __name__, url_prefix='/requestcall')
from app import basic_auth  # NOQA


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
    if response not in ['accepted', 'declined']:
        app.logger.info(f'unknown response: {response}')
        return jsonify({'error': True, 'message': 'unknown response'}), 400
    app.logger.info(f'response for buyer {buyer_id}: {response}')
    app.redis.set(f'response:{buyer_id}', response)
    # TODO timed out
    return '', 200


@requestcall.route('/', methods=['POST'])
def post_requestcall():
    data = request.get_json()
    phone = data.get('phoneNumber')
    public_id = data.get('sellerId')
    buyer_id = data.get('sessionId')

    app.logger.info(data)
    if phone is None or public_id is None:
        return jsonify({'error': True, 'message': 'you must specify phoneNumber and sellerId'}), 400
    if not valid_phone(phone):
        return jsonify({'error': True, 'message': 'phoneNumber is not valid'}), 400

    user = Location.query.filter_by(public_id=public_id).first()
    if user is None:
        return jsonify({'error': True, 'message': 'no user found'}), 404

    webhook = Webhook(app.config['WEBHOOK_URL'])

    app.logger.info(f'sending requestcall for buyer {buyer_id}')
    if not webhook.send_contact_request(user.id, buyer_id, phone):
        app.logger.info('requestcall failed')
        return jsonify({'success': False, 'error': True}), 500
    end_time = datetime.now() + timedelta(seconds=60)
    while True:
        app.logger.info('waiting')
        response = app.redis.get(f'response:{buyer_id}')
        if datetime.now() >= end_time:
            app.logger.info('requestcall no response')
            return jsonify({'success': False})
        if response == 'accepted':
            app.redis.delete(f'response:{buyer_id}')
            app.logger.info('requestcall accepted')
            return jsonify({'success': True})
        elif response == 'declined':
            app.redis.delete(f'response:{buyer_id}')
            app.logger.info('requestcall delcined')
            return jsonify({'success': False})
        sleep(1)
