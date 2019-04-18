import pytest
from unittest.mock import patch, MagicMock
from config import Testing as config
from redismap import RedisMap


@pytest.fixture(scope='function')
def redis_map(redis_conn):
    yield RedisMap(MagicMock(), redis_conn)
    redis_conn.flushdb()


@pytest.fixture(scope='function')
def redis_mock(redis_conn):
    return MagicMock()


@pytest.fixture(scope='function')
def redis_map_mock(redis_mock):
    yield RedisMap(MagicMock(), redis_mock)


def test_add_user_uses_setex(redis_mock, redis_map_mock):
    redis_map_mock.add_or_update_user(999)

    redis_mock.setex.assert_called_with('user:Q2k23', 300, '999')


def test_update_user_location_uses_geoadd(redis_mock, redis_map_mock):
    redis_map_mock.update_user_location(999, 60.0, 24.0, initials='A A')

    redis_mock.geoadd.assert_called_with('loc', 60.0, 24.0, 'Q2k23')


def test_expire_locations_removes_user(redis_mock, redis_map_mock):
    zscan_iter = [[('1krgZy', 3716815713752047.0), ('3eA43', 3716815713752047.0)]]
    exists = side_eddects = [1, 0]  # returns 1, then 0
    redis_mock.exists.side_effect = exists
    redis_mock.zscan_iter.side_effect = zscan_iter

    redis_map_mock.expire_locations()

    redis_mock.zrem.assert_called_with('loc', '3eA43')
