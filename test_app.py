import os
import pytest
from unittest.mock import patch
from base64 import b64encode
from app import app as app
from config import Testing as config


@pytest.fixture
def client():
    # app.config.from_object('config.Testing')
    client = app.test_client()
    yield client


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


def test_response_schema(client, dummylocation):
    r = client.get('/', headers=with_auth())
    assert r.get_json() == {
        "type": "Feature",
        "geometry": {
            "type": "Point",
            "coordinates": [60.0, 65.5]
        },
        "properties": {
            "name": "dummy"
        }
    }
