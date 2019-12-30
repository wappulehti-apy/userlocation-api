import os
import pytest
from unittest.mock import patch, MagicMock
from helpers import with_auth


def test_set_requires_authentication(client):
    r = client.post('/locations/123')
    assert r.status == '401 UNAUTHORIZED'


def test_set_authentication_works(client):
    r = client.post(f'/locations/123?latitude=60.0&longitude=24.0&nick=B%20A', headers=with_auth())
    assert r.status == '200 OK'


def test_response_is_json(client):
    r = client.get('/locations', headers=with_auth())
    assert r.headers["Content-Type"] == "application/json"


def test_get_locations(client, map_with_data):
    r = client.get('/locations')
    assert r.get_json() == {'users': [
        {'id': 'R3Ea3', 'nick': 'A A', 'location': {'lat': 60.16952, 'lon': 24.93545}},
        {'id': 'O6zkQ', 'nick': 'B B', 'location': {'lat': 59.33258, 'lon': 18.0649}}
    ]}


def test_set_location(client, redis_map, redis_conn):
    user_id = 123
    data = {
        'latitude': 60.16952,
        'longitude': 24.93545,
        'nick': 'B A'
    }
    r = client.post(f'/locations/{user_id}', json=data, headers=with_auth())

    assert len(redis_conn.data['loc']) == 1
    print(redis_conn.data['loc'])
    location = redis_conn.data['loc']['3GOM3']
    assert location[0] == 24.93545
    assert location[1] == 60.16952
    assert redis_conn.get('nick:3GOM3') == 'B A'


def test_set_location_validates_args(client, redis_map, redis_conn):
    r = client.post(f'/locations/123', json={'foo': 'bar', 'nick': 'A A'}, headers=with_auth())
    json = r.get_json()

    assert r.status == '400 BAD REQUEST'
    assert json['error']
    assert json['message'] == 'Bad Request'


def test_tests_dont_leak(client, redis_conn):
    """Ensure loc is still None"""
    locations = redis_conn.data.get('loc')
    assert locations is None

# def test_location_expires(client, db_with_data):
#     pass


def test_set_location_updates_existing(client, redis_map, map_with_data):
    original = redis_map.get_locations_named(0, 0)[0]
    assert original.coordinate.longitude == 24.93545
    assert original.nick == "A A"
    data = {
        'latitude': 60.16952,
        'longitude': 30.00000,
        'nick': 'B B'
    }
    r = client.post(f'/locations/1', json=data, headers=with_auth())
    new = redis_map.get_locations_named(0, 0)[0]
    assert new.coordinate.longitude == 30.00000
    assert new.nick == "B B"


def test_empty_response(client):
    r = client.get('/locations')
    assert r.get_json() == {'users': []}


def test_response_schema(client, map_with_data):
    """Checks that output is as expected."""
    r = client.get('/locations')
    assert r.get_json() == {'users': [
        {'id': 'R3Ea3', 'nick': 'A A', 'location': {'lat': 60.16952, 'lon': 24.93545}},
        {'id': 'O6zkQ', 'nick': 'B B', 'location': {'lat': 59.33258, 'lon': 18.0649}}
    ]}


def test_remove_location(client, redis_map, redis_conn, map_with_data):
    assert len(redis_conn.data['loc']) == 2
    r = client.delete(f'/locations/1', headers=with_auth())

    assert len(redis_conn.data['loc']) == 1