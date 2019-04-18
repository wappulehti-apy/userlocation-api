import pytest
from unittest.mock import patch, MagicMock
from config import Testing as config
from redismap import RedisMap


@pytest.fixture(scope='function')
def redis_map(redis_conn):
    yield RedisMap(redis_conn)
    redis_conn.flushdb()


@pytest.fixture(scope='function')
def redis_mock(redis_conn):
    return MagicMock()


@pytest.fixture(scope='function')
def redis_map_mock(redis_mock):
    yield RedisMap(redis_mock)


def test_add_user_uses_setex(redis_mock, redis_map_mock):
    redis_map_mock.add_or_update_user(999)

    redis_mock.setex.assert_called_with('user:999', 300, 'Q2k23')


def test_update_user_location_uses_geoadd(redis_mock, redis_map_mock):
    redis_map_mock.update_user_location(999, 60.0, 24.0)

    redis_mock.geoadd.assert_called_with('999', 60.0, 24.0)


def test_update_user_location_uses_geoadd(redis_mock, redis_map_mock):
    redis_map_mock.update_user_location(999, 60.0, 24.0)

    redis_mock.setex.assert_called_with('user:999', 300, 'Q2k23')

# def test_expire_locations_removes_user(client, redis_conn, redis_map):
#     redis_conn.geoadd('loc', 60.0, 24.0, '999')
#     #self.r.zscore()
#     redis_map.expire_locations()
# pubsub.subscribe("__keyspace@0__:*")
