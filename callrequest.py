import re
from gevent import sleep
import uuid
from datetime import datetime, timedelta
from flask import current_app as app
from flask import Blueprint, request, jsonify, session

from models import Location
from webhook import Webhook
from database import db

callrequest = Blueprint('callrequest', __name__, url_prefix='/callrequest')
from app import basic_auth  # NOQA


def valid_phone(phone):
    if len(phone) < 6 or len(phone) > 15:
        return False
    # Must contain at least 3 numbers
    if not re.search(r"\d\d\d", phone):
        return False
    return True


@callrequest.route('/', methods=['POST'])
def post_callrequest():
    data = request.get_json()
    phone = data.get('phoneNumber')
    public_id = data.get('sellerId')
    if 'id' not in session:
        session['id'] = uuid.uuid4()
    buyer_id = session['id']

    if phone is None or public_id is None:
        return jsonify({'error': True, 'message': 'you must specify phoneNumber and sellerId'}), 400
    if not valid_phone(phone):
        return jsonify({'error': True, 'message': 'phoneNumber is not valid'}), 400

    user = Location.query.filter_by(public_id=public_id).first()
    if user is None:
        return jsonify({'error': True, 'message': 'no user found'}), 404

    webhook = Webhook(app.config['WEBHOOK_URL'])

    app.logger.info(f'sending callrequest for buyer {buyer_id}')
    if not webhook.send_contact_request(user.id, buyer_id, phone):
        app.logger.info('callrequest failed')
        return jsonify({'success': False, 'error': True})
    end_time = datetime.now() + timedelta(seconds=60)
    while True:
        app.logger.info('waiting')
        response = app.redis.get(f'response:{buyer_id}')
        if datetime.now() >= end_time:
            app.logger.info('callrequest no response')
            return jsonify({'success': False})
        if response == 'accepted':
            app.logger.info('callrequest accepted')
            return jsonify({'success': True})
        elif response == 'declined':
            app.logger.info('callrequest delcined')
            return jsonify({'success': False})
        sleep(1)
