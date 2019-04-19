import pytest
from unittest.mock import patch, MagicMock, call
from config import Testing as config
from redismap import RedisMap, Location


@pytest.fixture(scope='function')
def redis_map(redis_conn):
    yield RedisMap(MagicMock(), redis_conn)
    redis_conn.flushdb()


def test_add_user_uses_setex(redis_mock, redis_map_mock):
    redis_map_mock.add_or_update_user(999, 'A A')

    assert redis_mock.setex.mock_calls == [
        call('user:Q2k23', 300, '999'),
        call('initials:Q2k23', 300, 'A A')
    ]


def test_update_user_location_uses_geoadd(redis_mock, redis_map_mock):
    redis_map_mock.update_user_location(999, 24.0, 60.0, initials='A A')

    redis_mock.geoadd.assert_called_with('loc', 24.0, 60.0, 'Q2k23')


def test_expire_locations_removes_user(redis_mock, redis_map_mock):
    zscan_iter = [[('1krgZy', 3716815713752047.0), ('3eA43', 3716815713752047.0)]]
    exists = side_eddects = [1, 0]  # returns 1, then 0
    redis_mock.exists.side_effect = exists
    redis_mock.zscan_iter.side_effect = zscan_iter

    redis_map_mock.expire_locations()

    redis_mock.zrem.assert_called_with('loc', '3eA43')


def test_get_locations_returns_users(redis_mock, redis_map_mock):
    redis_mock.get.side_effect = ['A A']
    redis_mock.georadius.side_effect = [[('R3Ea3', [24.0, 60.0])]]

    locations = redis_map_mock.get_locations(0, 0)

    assert locations == [
        ('R3Ea3', [24.0, 60.0], 'A A')
    ]
    redis_mock.get.assert_called_with('initials:R3Ea3')


def test_get_locations_does_not_return_expired_users(redis_mock, redis_map_mock):
    redis_mock.get.side_effect = ['A A', None]
    redis_mock.georadius.side_effect = [[('R3Ea3', [24.0, 60.0]), ('O6zkQ', [25.0, 59.0])]]

    locations = redis_map_mock.get_locations(0, 0)

    assert locations == [
        ('R3Ea3', [24.0, 60.0], 'A A')
    ]
    assert redis_mock.get.mock_calls == [
        call('initials:R3Ea3'),
        call('initials:O6zkQ')
    ]


def test_get_locations_named_returns_named_tuple(redis_mock, redis_map_mock):
    redis_mock.get.side_effect = ['A A']
    redis_mock.georadius.side_effect = [[('R3Ea3', [24.0, 60.0])]]

    locations = redis_map_mock.get_locations_named(0, 0)

    assert locations == [
        Location('R3Ea3', 24.0, 60.0, 'A A')
    ]


def test_user_exists(redis_map, redis_conn, map_with_data):
    assert redis_map.user_exists('R3Ea3')
    assert redis_map.user_exists('NOPE') == False


def test_user_id(redis_map, redis_conn, map_with_data):
    assert isinstance(redis_map.user_id('R3Ea3'), int)
    assert redis_map.user_id('R3Ea3') == 1
    assert redis_map.user_id('O6zkQ') == 2
    assert redis_map.user_id('NOPE') is None
