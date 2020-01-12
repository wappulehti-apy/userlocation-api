import os
import pytest
from unittest.mock import patch, MagicMock
from helpers import with_auth


# get /locations
def test_get_response_is_json(client):
    r = client.get('/locations', headers=with_auth())
    assert r.headers["Content-Type"] == "application/json"


def test_get_locations(client, map_with_data):
    r = client.get('/locations')
    assert r.get_json() == {'users': [
        {'public_id': 'hashof1', 'nick': 'Abe', 'location': {'lat': 60.16952, 'lon': 24.93545}},
        {'public_id': 'hashof2', 'nick': 'Bob', 'location': {'lat': 59.33258, 'lon': 18.0649}}
    ]}


def test_get_locations_near_given_coordinates(client, map_with_data):
    r = client.get('/locations?longitude=0.000000&latitude=0.000000')
    assert r.get_json() == {'users': []}


def test_get_empty_response(client):
    r = client.get('/locations')
    assert r.get_json() == {'users': []}


def test_get_response_schema(client, map_with_data):
    """Checks that output is as expected."""
    r = client.get('/locations')
    assert r.get_json() == {'users': [
        {'public_id': 'hashof1', 'nick': 'Abe', 'location': {'lat': 60.16952, 'lon': 24.93545}},
        {'public_id': 'hashof2', 'nick': 'Bob', 'location': {'lat': 59.33258, 'lon': 18.0649}}
    ]}


# post /locations
def test_post_requires_authentication(client):
    r = client.post('/locations/123')
    assert r.status == '401 UNAUTHORIZED'


def test_post_authentication_works(client):
    r = client.post(f'/locations/123?latitude=60.0&longitude=24.0&nick=B%20A', headers=with_auth())
    assert r.status == '200 OK'


def test_post_location(client, redis_map, redis_conn):
    user_id = 123
    data = {
        'latitude': 60.16952,
        'longitude': 24.93545,
        'nick': 'Changed'
    }
    r = client.post(f'/locations/{user_id}', json=data, headers=with_auth())

    assert len(redis_conn.data['loc']) == 1
    location = redis_conn.data['loc']['hashof123']
    assert location[0] == 24.93545
    assert location[1] == 60.16952
    assert redis_conn.get('nick:hashof123') == 'Changed'


def test_post_location_validates_arg_presence(client, redis_map, redis_conn):
    r = client.post(f'/locations/123', json={'foo': 'bar', 'nick': 'Abe'}, headers=with_auth())
    json = r.get_json()

    assert r.status == '400 BAD REQUEST'
    assert json['error']
    assert json['message'].startswith('invalid longitude')


def test_post_location_validates_arg_type(client, redis_map, redis_conn):
    r = client.post(f'/locations/123', json={'longitude': 'foo', 'latitude': 'bar', 'nick': 'Abe'}, headers=with_auth())
    json = r.get_json()

    assert r.status == '400 BAD REQUEST'
    assert json['error']
    assert json['message'].startswith('invalid longitude: please specify longitude in format')


def test_post_location_validates_coordnates(client, redis_map, redis_conn):
    # Valid coordinates
    r = client.post(f'/locations/123', json={'longitude': 24.93545, 'latitude': 60.16952, 'nick': 'Abe'}, headers=with_auth())
    assert r.status == '200 OK'

    # Invalid longitude
    r = client.post(f'/locations/123', json={'longitude': 181.0000, 'latitude': 60.16952, 'nick': 'Abe'}, headers=with_auth())
    json = r.get_json()
    assert r.status == '400 BAD REQUEST'
    assert json['error']
    assert json['message'].startswith('invalid longitude')

    # Invalid latitude
    r = client.post(f'/locations/123', json={'longitude': 24.93545, 'latitude': 91.000000, 'nick': 'Abe'}, headers=with_auth())
    json = r.get_json()
    assert r.status == '400 BAD REQUEST'
    assert json['message'].startswith('invalid latitude')


def test_tests_dont_leak(client, redis_conn):
    """Ensure loc is still None"""
    locations = redis_conn.data.get('loc')
    assert locations is None

# def test_location_expires(client, db_with_data):
#     pass


def test_post_location_updates_existing(client, redis_map, map_with_data):
    original = redis_map.get_locations_named(24, 60)[0]
    assert original.coordinate.longitude == 24.93545
    assert original.nick == "Abe"
    data = {
        'latitude': 60.16952,
        'longitude': 30.00000,
        'nick': 'Changed'
    }
    r = client.post(f'/locations/1', json=data, headers=with_auth())
    new = redis_map.get_locations_named(24, 60)[0]
    assert new.coordinate.longitude == 30.00000
    assert new.nick == "Changed"


# delete /locations
def test_remove_location(client, redis_map, redis_conn, map_with_data):
    assert len(redis_conn.data['loc']) == 2
    r = client.delete(f'/locations/1', headers=with_auth())

    assert len(redis_conn.data['loc']) == 1
