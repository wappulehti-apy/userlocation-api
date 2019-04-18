import pytest
from unittest.mock import patch, MagicMock
from config import Testing as config
from redismap import RedisMap


@pytest.fixture(scope='function')
def redis_map(redis_conn):
    yield RedisMap(None, redis_conn)
    redis_conn.flushdb()


@pytest.fixture(scope='function')
def redis_mock(redis_conn):
    return MagicMock()


@pytest.fixture(scope='function')
def redis_map_mock(redis_mock):
    yield RedisMap(None, redis_mock)


def test_add_user_uses_setex(redis_mock, redis_map_mock):
    redis_map_mock.add_or_update_user(999)

    redis_mock.setex.assert_called_with('user:Q2k23', 300, '999')


def test_update_user_location_uses_geoadd(redis_mock, redis_map_mock):
    redis_map_mock.update_user_location(999, 60.0, 24.0, initials='A A')

    redis_mock.geoadd.assert_called_with('loc', 60.0, 24.0, 'Q2k23')
