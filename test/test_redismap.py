import pytest
from unittest.mock import patch, MagicMock, call
from redismap import RedisMap, Location, Coordinate


@pytest.fixture(scope='function')
def redis_map(redis_conn):
    yield RedisMap(MagicMock(), redis_conn)
    # Ensure redis is empty
    redis_conn.flushdb()
    redis_conn.data = {}


def test_add_user_uses_setex(redis_mock, redis_map_mock):
    redis_map_mock.add_or_update_user(999, 'Abe')

    assert redis_mock.setex.mock_calls == [
        call('user:hashof999', 900, '999'),
        call('nick:hashof999', 900, 'Abe')
    ]


def test_update_user_location_uses_geoadd(redis_mock, redis_map_mock):
    redis_map_mock.update_user_location(999, 24.0, 60.0, nick='Abe')

    redis_mock.geoadd.assert_called_with('loc', 24.0, 60.0, 'hashof999')


def test_expire_locations_removes_user(redis_mock, redis_map_mock):
    zscan_iter = [[('hashof100', 3716815713752047.0), ('hashof101', 3716815713752047.0)]]
    exists = side_eddects = [1, 0]  # returns 1, then 0
    redis_mock.exists.side_effect = exists
    redis_mock.zscan_iter.side_effect = zscan_iter

    redis_map_mock.expire_locations()

    redis_mock.zrem.assert_called_with('loc', 'hashof101')


def test_get_locations_returns_users(redis_mock, redis_map_mock):
    redis_mock.get.side_effect = ['Abe']
    redis_mock.georadius.side_effect = [[('hashof1', [24.0, 60.0])]]

    locations = redis_map_mock.get_locations(0, 0)

    assert locations == [
        Location('hashof1', Coordinate(24.0, 60.0), 'Abe')
    ]
    redis_mock.get.assert_called_with('nick:hashof1')


def test_get_locations_does_not_return_expired_users(redis_mock, redis_map_mock):
    redis_mock.get.side_effect = ['Abe', None]
    redis_mock.georadius.side_effect = [[('hashof1', [24.0, 60.0]), ('hashof2', [25.0, 59.0])]]

    locations = redis_map_mock.get_locations(0, 0)

    assert locations == [
        Location('hashof1', Coordinate(24.0, 60.0), 'Abe')
    ]
    assert redis_mock.get.mock_calls == [
        call('nick:hashof1'),
        call('nick:hashof2')
    ]


def test_get_locations_named_returns_named_tuple(redis_mock, redis_map_mock):
    redis_mock.get.side_effect = ['Abe']
    redis_mock.georadius.side_effect = [[('hashof1', [24.0, 60.0])]]

    locations = redis_map_mock.get_locations_named(0, 0)

    assert locations == [
        Location('hashof1', Coordinate(24.0, 60.0), 'Abe')
    ]


def test_user_exists(redis_map, redis_conn, map_with_data):
    assert redis_map.user_exists('hashof1')
    assert redis_map.user_exists('NOPE') == False


def test_user_id(redis_map, redis_conn, map_with_data):
    assert isinstance(redis_map.user_id('hashof1'), int)
    assert redis_map.user_id('hashof1') == 1
    assert redis_map.user_id('hashof2') == 2
    assert redis_map.user_id('NOPE') is None
