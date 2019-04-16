import os
import pytest
from unittest.mock import patch, MagicMock
from base64 import b64encode
from app import app as app
from config import Testing as config
from database import db
from models import Location


@pytest.fixture(scope="function")
def db_with_data(db_session):
    location1 = Location(1, latitude=60.16952, longitude=24.93545, initials="A A")
    location2 = Location(2, latitude=59.33258, longitude=18.0649, initials="B B")
    db_session.add(location1)
    db_session.add(location2)
    db_session.commit()

    yield

    # Automatically rolled back by pytest-flask-sqlalchemy


@pytest.fixture
def dummylocation():
    return


def with_auth(original={}):
    username = config.BASIC_AUTH_USERNAME
    password = config.BASIC_AUTH_PASSWORD

    token = b64encode(bytes(username + ":" + password, 'ascii')).decode('ascii')
    auth = {"Authorization": "Basic {}".format(token)}

    return {**original, **auth}


def test_set_requires_authentication(client):
    r = client.get('/set/123')
    assert r.status == '401 UNAUTHORIZED'


def test_set_authentication_works(client, db_session):
    r = client.get(f'/set/123?latitude=60.0&longitude=24.0&initials=B%20A', headers=with_auth())
    assert r.status == '200 OK'


def test_response_is_json(client):
    r = client.get('/', headers=with_auth())
    assert r.headers["Content-Type"] == "application/json"


def test_get_locations(client, db_session, db_with_data):
    r = client.get('/', headers=with_auth())
    assert r.get_json() == {'sellers': [
        {'id': 'R3Ea3', 'initials': 'A A', 'location': {'lat': 60.16952, 'lon': 24.93545}},
        {'id': 'O6zkQ', 'initials': 'B B', 'location': {'lat': 59.33258, 'lon': 18.0649}}
    ]}


def test_callrequest_returns_success_true_on_success(client, db_session, db_with_data):
    with patch('requests.post') as post:
        post.return_value = MagicMock(status_code=200)
        r = client.post('/requestcall', json={'phoneNumber': '040 123456', 'sellerId': 'R3Ea3'})
    assert r.get_json() == {'success': True}


def test_callrequest_returns_success_false_on_failed_request(client, db_session, db_with_data):
    with patch('requests.post') as post:
        post.return_value = MagicMock(status_code=500)
        r = client.post('/requestcall', json={'phoneNumber': '040 123456', 'sellerId': 'R3Ea3'})
    assert r.get_json() == {'success': False}


def test_callrequest_returns_error_on_bad_id(client, db_session, db_with_data):
    r = client.post('/requestcall', json={'phoneNumber': '040 123456', 'sellerId': 'nonexistent'})
    assert r.get_json() == {'error': True, 'message': 'no user found'}
    assert r.status == '404 NOT FOUND'


def test_callrequest_returns_error_on_bad_phone(client, db_session, db_with_data):
    r = client.post('/requestcall', json={'phoneNumber': 'invalid', 'sellerId': 'R3Ea3'})
    assert r.get_json() == {'error': True, 'message': 'phoneNumber is not valid'}
    assert r.status == '400 BAD REQUEST'


def test_callrequest_calls_webhook_url(client, db_session, db_with_data):
    with patch('requests.post') as post:
        post.return_value = MagicMock(status_code=200)
        r = client.post('/requestcall', json={'phoneNumber': '040 123456', 'sellerId': 'R3Ea3'})
    args, kwargs = post.call_args
    assert args[0] == "https://example.com/webhook"


def test_set_location(client, db_session):
    user_id = 123
    r = client.get(f'/set/{user_id}?latitude=60.16952&longitude=24.93545&initials=B%20A', headers=with_auth())
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
    r = client.get(f'/set/1?latitude=60.16952&longitude=30.00000&initials=B%20B', headers=with_auth())
    new = Location.query.get(1)
    assert new.longitude == 30.00000
    assert new.initials == "B B"


def test_empty_response(client):
    r = client.get('/', headers=with_auth())
    assert r.get_json() == {'sellers': []}


def test_response_schema(client, db_session, db_with_data):
    r = client.get('/', headers=with_auth())
    assert r.get_json() == {'sellers': [
        {'id': 'R3Ea3', 'initials': 'A A', 'location': {'lat': 60.16952, 'lon': 24.93545}},
        {'id': 'O6zkQ', 'initials': 'B B', 'location': {'lat': 59.33258, 'lon': 18.0649}}
    ]}
