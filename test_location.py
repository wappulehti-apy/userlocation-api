import os
import pytest
from unittest.mock import patch, MagicMock
from base64 import b64encode
from config import Testing as config


def with_auth(original={}):
    username = config.BASIC_AUTH_USERNAME
    password = config.BASIC_AUTH_PASSWORD

    token = b64encode(bytes(username + ":" + password, 'ascii')).decode('ascii')
    auth = {"Authorization": "Basic {}".format(token)}

    return {**original, **auth}


def test_set_requires_authentication(client):
    r = client.get('/location/set/123')
    assert r.status == '401 UNAUTHORIZED'


def test_set_authentication_works(client):
    r = client.get(f'/location/set/123?latitude=60.0&longitude=24.0&initials=B%20A', headers=with_auth())
    assert r.status == '200 OK'


def test_response_is_json(client):
    r = client.get('/location', headers=with_auth())
    assert r.headers["Content-Type"] == "application/json"


def test_get_locations(client, map_with_data):
    r = client.get('/location/')  # , headers=with_auth())
    assert r.get_json() == {'sellers': [
        {'id': 'R3Ea3', 'initials': 'A A', 'location': {'lat': 60.16952, 'lon': 24.93545}},
        {'id': 'O6zkQ', 'initials': 'B B', 'location': {'lat': 59.33258, 'lon': 18.0649}}
    ]}


def test_get_locations_returns_callrequest_if_set(client, map_with_data, redis_conn):
    redis_conn.hmset(f'response:123', {'response': 'accepted', 'seller_id': 'Q2k23'})
    headers = {**with_auth(), 'sessionId': '123'}
    r = client.get('/location/', headers=headers)
    assert r.get_json() == {'sellers': [
        {'id': 'R3Ea3', 'initials': 'A A', 'location': {'lat': 60.16952, 'lon': 24.93545}},
        {'id': 'O6zkQ', 'initials': 'B B', 'location': {'lat': 59.33258, 'lon': 18.0649}}
    ],
        'callRequest': {'accepted': True, 'sellerId': 'Q2k23'}
    }


def test_set_location(client, redis_map, redis_conn):
    user_id = 123
    r = client.get(f'/location/set/{user_id}?latitude=60.16952&longitude=24.93545&initials=B%20A', headers=with_auth())

    assert len(redis_conn.data['loc']) == 1
    location = redis_conn.data['loc']['3GOM3']
    assert location[0] == 24.93545
    assert location[1] == 60.16952
    assert redis_conn.get('initials:3GOM3') == 'B A'


def test_tests_dont_leak(client, redis_conn):
    locations = redis_conn.data.get('loc')
    assert locations is None

# def test_location_expires(client, db_with_data):
#     pass


def test_set_location_updates_existing(client, redis_map, map_with_data):
    original = redis_map.get_locations_named(0, 0)[0]
    assert original.longitude == 24.93545
    assert original.initials == "A A"
    r = client.get(f'/location/set/1?latitude=60.16952&longitude=30.00000&initials=B%20B', headers=with_auth())
    new = redis_map.get_locations_named(0, 0)[0]
    assert new.longitude == 30.00000
    assert new.initials == "B B"


def test_empty_response(client):
    r = client.get('/location')
    assert r.get_json() == {'sellers': []}


def test_response_schema(client, map_with_data):
    r = client.get('/location')
    assert r.get_json() == {'sellers': [
        {'id': 'R3Ea3', 'initials': 'A A', 'location': {'lat': 60.16952, 'lon': 24.93545}},
        {'id': 'O6zkQ', 'initials': 'B B', 'location': {'lat': 59.33258, 'lon': 18.0649}}
    ]}
