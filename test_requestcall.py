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


def test_requestcall_returns_success_true_on_success(client, map_with_data, redis_conn):
    with patch('requests.post', return_value=MagicMock(status_code=200)):
        r = client.post('/requestcall', json={'phoneNumber': '040 123456', 'sellerId': 'R3Ea3'}, headers={'sessionId': '123'})
    assert r.get_json() == {'success': True}


def test_requestcall_returns_error_on_failed_request(client, map_with_data):
    with patch('requests.post') as post:
        post.return_value = MagicMock(status_code=500)
        r = client.post('/requestcall', json={'phoneNumber': '040 123456', 'sellerId': 'R3Ea3'}, headers={'sessionId': '123'})
    assert r.get_json() == {'error': True, 'success': False}


def test_requestcall_reads_buyer_id_from_session_id(client, map_with_data, redis_conn):
    redis_conn.hmset(f'response:100', {'response': 'accepted', 'user_id': '999'})

    # with client.session_transaction() as sess:
    #     sess['id'] = '100'

    with patch('requests.post') as post:
        post.return_value = MagicMock(status_code=200)
        r = client.post('/requestcall', json={'phoneNumber': '040 123456', 'sellerId': 'R3Ea3'}, headers={'sessionId': '100'})
    assert r.get_json() == {'success': True}


# def test_requestcall_returns_success_false_on_decline(client, db_session, db_with_data, redis_conn):
#     redis_conn.hmset(f'response:100', {'response':'declined', 'user_id':'999'})

#     with patch('requests.post') as post:
#         post.return_value = MagicMock(status_code=200)
#         r = client.post('/requestcall', json={'phoneNumber': '040 123456', 'sellerId': 'R3Ea3'}, headers={'sessionId': '123'})
#     assert r.get_json() == {'success': False}


def test_requestcall_returns_error_on_bad_id(client, map_with_data):
    r = client.post('/requestcall', json={'phoneNumber': '040 123456', 'sellerId': 'nonexistent'})
    assert r.get_json() == {'error': True, 'message': 'no user found'}
    assert r.status == '404 NOT FOUND'


def test_requestcall_returns_error_on_bad_phone(client, map_with_data, redis_conn):
    redis_conn.hmset(f'response:100', {'response': 'accepted', 'user_id': '999'})
    r = client.post('/requestcall', json={'phoneNumber': 'invalid', 'sellerId': 'R3Ea3'}, headers={'sessionId': '123'})
    assert r.get_json() == {'error': True, 'message': 'phoneNumber is not valid'}
    assert r.status == '400 BAD REQUEST'


def test_requestcall_calls_webhook_url(client, map_with_data, redis_conn):
    with patch('requests.post', return_value=MagicMock(status_code=200)) as post:
        r = client.post('/requestcall', json={'phoneNumber': '040 123456', 'sellerId': 'R3Ea3'}, headers={'sessionId': '123'})
    args, kwargs = post.call_args
    assert args[0] == "https://example.com/webhook"


def test_respond_requestcall_requires_auth(client, map_with_data):
    r = client.post('/requestcall/respond', json={'buyerId': '123asd', 'response': 'nonexistent'})
    assert r.status == '401 UNAUTHORIZED'


def test_respond_requestcall_returns_error_on_bad_response(client, map_with_data):
    headers = {**with_auth(), 'sessionId': '123'}
    r = client.post('/requestcall/respond', json={'buyerId': '123asd', 'response': 'nonexistent'}, headers=headers)
    assert r.status == '400 BAD REQUEST'


def test_respond_requestcall_sets_response_in_redis(client, map_with_data, redis_conn):
    with patch('requests.post', return_value=MagicMock(status_code=200)) as post,\
            patch.object(redis_conn, 'hmset') as redis_hmset:
        r = client.post('/requestcall/respond', json={'buyerId': '123asd', 'response': 'accepted', 'userId': '999'}, headers=with_auth())
        redis_hmset.assert_called()
        redis_hmset.assert_called_with('response:123asd', {'response': 'accepted', 'seller_id': 'Q2k23'})
    assert r.status == '200 OK'
