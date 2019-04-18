import os
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


def test_set_requires_authentication(client):
    r = client.get('/location/set/123')
    assert r.status == '401 UNAUTHORIZED'


def test_set_authentication_works(client, db_session):
    r = client.get(f'/location/set/123?latitude=60.0&longitude=24.0&initials=B%20A', headers=with_auth())
    assert r.status == '200 OK'


def test_response_is_json(client):
    r = client.get('/location', headers=with_auth())
    assert r.headers["Content-Type"] == "application/json"


def test_get_locations(client, db_session, db_with_data):
    r = client.get('/location/')  # , headers=with_auth())
    assert r.get_json() == {'sellers': [
        {'id': 'R3Ea3', 'initials': 'A A', 'location': {'lat': 60.16952, 'lon': 24.93545}},
        {'id': 'O6zkQ', 'initials': 'B B', 'location': {'lat': 59.33258, 'lon': 18.0649}}
    ]}


def test_get_locations_returns_callrequest_if_set(client, db_session, db_with_data, redis_conn):
    redis_conn.hmset(f'response:123', {'response': 'accepted', 'seller_id': 'Q2k23'})
    headers = {**with_auth(), 'sessionId': '123'}
    r = client.get('/location/', headers=headers)
    assert r.get_json() == {'sellers': [
        {'id': 'R3Ea3', 'initials': 'A A', 'location': {'lat': 60.16952, 'lon': 24.93545}},
        {'id': 'O6zkQ', 'initials': 'B B', 'location': {'lat': 59.33258, 'lon': 18.0649}}
    ],
        'callRequest': {'accepted': True, 'sellerId': 'Q2k23'}
    }


def test_set_location(client, db_session):
    user_id = 123
    r = client.get(f'/location/set/{user_id}?latitude=60.16952&longitude=24.93545&initials=B%20A', headers=with_auth())
    locations = Location.query.all()
    assert len(locations) == 1
    assert locations[0].id == user_id
    assert locations[0].initials == 'B A'
    assert locations[0].latitude == 60.16952
    assert locations[0].longitude == 24.93545


def test_tests_dont_leak(client, db_session):
    locations = Location.query.all()
    assert len(locations) == 0

# def test_location_expires(client, db_with_data):
#     pass


def test_set_location_updates_existing(client, db_session, db_with_data):
    original = Location.query.get(1)
    assert original.longitude == 24.93545
    assert original.initials == "A A"
    r = client.get(f'/location/set/1?latitude=60.16952&longitude=30.00000&initials=B%20B', headers=with_auth())
    new = Location.query.get(1)
    assert new.longitude == 30.00000
    assert new.initials == "B B"


def test_empty_response(client):
    r = client.get('/location')
    assert r.get_json() == {'sellers': []}


def test_response_schema(client, db_session, db_with_data):
    r = client.get('/location')
    assert r.get_json() == {'sellers': [
        {'id': 'R3Ea3', 'initials': 'A A', 'location': {'lat': 60.16952, 'lon': 24.93545}},
        {'id': 'O6zkQ', 'initials': 'B B', 'location': {'lat': 59.33258, 'lon': 18.0649}}
    ]}
