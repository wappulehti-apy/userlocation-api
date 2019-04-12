import os
import pytest
from unittest.mock import patch
from base64 import b64encode
from app import app as app
from config import Testing as config
from database import db
from models import Location


@pytest.fixture
def client():
    # app.config.from_object('config.Testing')
    client = app.test_client()
    # Establish an application context before running the tests.
    # ctx = app.app_context()
    # ctx.push()
    with app.app_context():
        db.create_all()
    yield client
    # ctx.pop()


@pytest.fixture(scope="function")
def db_with_data(client):
    location1 = Location(1, latitude=60.16952, longitude=24.93545, initials="A A")
    location2 = Location(2, latitude=59.33258, longitude=18.0649, initials="B B")
    with app.app_context():
        db.session.add(location1)
        db.session.add(location2)
        db.session.commit()
    yield
    with app.app_context():
        db.session.rollback()


@pytest.fixture
def dummylocation():
    return


def with_auth(original={}):
    username = config.BASIC_AUTH_USERNAME
    password = config.BASIC_AUTH_PASSWORD

    token = b64encode(bytes(username + ":" + password, 'ascii')).decode('ascii')
    auth = {"Authorization": "Basic {}".format(token)}

    return {**original, **auth}


def test_requires_authentication(client):
    r = client.get('/')
    assert r.status == '401 UNAUTHORIZED'


def test_authentication_works(client):
    r = client.get('/', headers=with_auth())
    assert r.status == '200 OK'


def test_response_is_json(client):
    r = client.get('/', headers=with_auth())
    assert r.headers["Content-Type"] == "application/json"


def test_get_locations(client, db_with_data):
    r = client.get('/', headers=with_auth())
    assert r.get_json() == {'locations': [
        {'initials': 'A A', 'location': {'lat': 60.16952, 'lon': 24.93545}},
        {'initials': 'B B', 'location': {'lat': 59.33258, 'lon': 18.0649}}
    ]}

# def test_response_schema(client, dummylocation):
#     r = client.get('/', headers=with_auth())
#     assert r.get_json() == {
#         "type": "Feature",
#         "geometry": {
#             "type": "Point",
#             "coordinates": [60.0, 65.5]
#         },
#         "properties": {
#             "name": "dummy"
#         }
#     }
