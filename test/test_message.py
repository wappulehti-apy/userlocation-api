import os
import pytest
from unittest.mock import patch, MagicMock
from helpers import with_auth

_DUMMY_CLIENT_ID = 'a' * 25
_VALID_DATA = {
    'user_id': 'hashof1',
    'message': '040123456'
}


def with_client_id():
    return {'clientId': _DUMMY_CLIENT_ID}


# get /message
def test_get_message_requires_client_id(client):
    r = client.get('/message')
    assert r.status == '401 UNAUTHORIZED'


def test_get_message(client, redis_conn):
    response = {'public_id': 'hashof1', 'data': 'accepted'}

    redis_conn.hmset(f'response:{_DUMMY_CLIENT_ID}', response)

    r = client.get('/message', headers=with_client_id())
    assert r.get_json() == {'response': {'public_id': 'hashof1', 'data': 'accepted'}}


def test_get_message_deletes_received_received_message_from_redis(client, redis_conn):
    redis_conn.hmset(f'response:{_DUMMY_CLIENT_ID}', {'foo': 'bar'})

    r = client.get('/message', headers=with_client_id())
    assert r.get_json() == {'response': {'foo': 'bar'}}
    r = client.get('/message', headers=with_client_id())
    assert r.get_json() == {'response': {}}


# post /message
def test_post_message_requires_client_id(client):
    r = client.post('/message')
    assert r.status == '401 UNAUTHORIZED'


def test_post_message_calls_webhook_url(client, map_with_data, redis_conn):
    with patch('requests.post', return_value=MagicMock(status_code=200)) as post:
        r = client.post('/message', json=_VALID_DATA, headers=with_client_id())
    args, kwargs = post.call_args
    assert args[0] == "https://example.com/webhook"

# def test_set_webhook_payload_is_correct(client, map_with_data, redis_conn):
#     with patch('requests.post', return_value=MagicMock(status_code=200)) as post:
#         r = client.post('/message', json=_VALID_DATA, headers={'sessionId': '123', **with_client_id()})
#     args, kwargs = post.call_args
#     json = kwargs['json']

#     assert json['example'] == True


def test_post_message_returns_success_on_success(client, map_with_data):
    with patch('requests.post') as post:
        post.return_value = MagicMock(status_code=200)
        r = client.post('/message', json=_VALID_DATA, headers=with_client_id())
    assert r.get_json() == {'success': True}


def test_post_message_returns_error_on_failure(client, map_with_data):
    with patch('requests.post') as post:
        post.return_value = MagicMock(status_code=500)
        r = client.post('/message', json=_VALID_DATA, headers=with_client_id())
    assert r.get_json() == {'error': True, 'success': False}


def test_post_message_validates_message(client):
    with patch('requests.post', return_value=MagicMock(status_code=200)) as post:
        r = client.post('/message', json={'user_id': 'foobar', 'message': 'notvalid'}, headers=with_client_id())
        assert r.get_json()['message'].startswith('invalid message')

        r = client.post('/message', json={'user_id': 'foobar', 'message': '123'}, headers=with_client_id())
        assert r.get_json()['message'].startswith('invalid message')

        r = client.post('/message', json={'user_id': 'foobar', 'message': '040123456'}, headers=with_client_id())
        assert r.get_json() == {'success': True}

        r = client.post('/message', json={'user_id': 'foobar', 'message': '+12 (34)-56789'}, headers=with_client_id())
        assert r.get_json() == {'success': True}


# post /message/<client_id>
def test_post_response_requires_authentication(client):
    r = client.post('/message/123')
    assert r.status == '401 UNAUTHORIZED'


def test_post_response(client, redis_conn):
    response = {'user_id': 1, 'response': 'accepted'}
    with patch.object(redis_conn, 'hmset') as redis_hmset:
        r = client.post('/message/' + _DUMMY_CLIENT_ID, json=response, headers=with_auth())

    assert r.status == '200 OK'
    redis_hmset.assert_called_with('response:' + _DUMMY_CLIENT_ID, {'response': 'accepted', 'user_id': 'hashof1'})