import pytest
from unittest.mock import patch, MagicMock
from base64 import b64encode
from config import Testing as config
from database import db
from models import Location


def with_auth(original={}):
    username = config.BASIC_AUTH_USERNAME
    password = config.BASIC_AUTH_PASSWORD

    token = b64encode(bytes(username + ":" + password, 'ascii')).decode('ascii')
    auth = {"Authorization": "Basic {}".format(token)}

    return {**original, **auth}


def test_callrequest_returns_success_true_on_success(client, db_session, db_with_data, redis_conn):
    with patch('requests.post', return_value=MagicMock(status_code=200)) as post,\
            patch.object(redis_conn, 'get', return_value='accepted'):
        r = client.post('/callrequest', json={'phoneNumber': '040 123456', 'sellerId': 'R3Ea3'})
    assert r.get_json() == {'success': True}


def test_callrequest_returns_success_false_on_failed_request(client, db_session, db_with_data):
    with patch('requests.post') as post:
        post.return_value = MagicMock(status_code=500)
        r = client.post('/callrequest', json={'phoneNumber': '040 123456', 'sellerId': 'R3Ea3'})
    assert r.get_json() == {'success': False}


def test_callrequest_returns_error_on_bad_id(client, db_session, db_with_data):
    r = client.post('/callrequest', json={'phoneNumber': '040 123456', 'sellerId': 'nonexistent'})
    assert r.get_json() == {'error': True, 'message': 'no user found'}
    assert r.status == '404 NOT FOUND'


def test_callrequest_returns_error_on_bad_phone(client, db_session, db_with_data, redis_conn):
    redis_conn.set(f'response:123', 'accepted')
    r = client.post('/callrequest', json={'phoneNumber': 'invalid', 'sellerId': 'R3Ea3'})
    assert r.get_json() == {'error': True, 'message': 'phoneNumber is not valid'}
    assert r.status == '400 BAD REQUEST'


def test_callrequest_calls_webhook_url(client, db_session, db_with_data, redis_conn):
    redis_conn.set(f'response:123', 'accepted')
    with patch('requests.post', return_value=MagicMock(status_code=200)) as post,\
            patch.object(redis_conn, 'get', return_value='accepted'):
        r = client.post('/callrequest', json={'phoneNumber': '040 123456', 'sellerId': 'R3Ea3'})
    args, kwargs = post.call_args
    assert args[0] == "https://example.com/webhook"
