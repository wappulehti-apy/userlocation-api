import pytest
from unittest.mock import patch, MagicMock
from fakeredis import FakeRedis
from api import create_app
from redismap import RedisMap


@pytest.fixture(scope='session')
def redis_conn():
    class AugmentedFakeredis(FakeRedis):
        "implements geoadd, georadius and zrem for FakeRedis"

        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.data = {}

        def geoadd(self, key, longitude, latitude, value):
            assert isinstance(key, str)
            assert isinstance(value, str)
            insert = [longitude, latitude]

            self.data.setdefault(key, {})
            self.data[key] = {value: insert}

        def georadius(self, key, longitude, latitude, radius, **kwargs):
            assert isinstance(key, str)
            try:
                return [(id, coordinates) for id, coordinates in self.data.get(key).items()]
            except AttributeError:
                return []

        def zrem(self, key, value):
            self.data[key].pop(value, None)

    return AugmentedFakeredis(decode_responses=True)


@pytest.fixture(scope='session')
def app(redis_conn):
    _app = create_app(redis_conn=redis_conn)
    yield _app


@pytest.fixture(scope='function')
def client(app):
    client = app.test_client()

    # Establish an application context before running the tests.
    ctx = app.app_context()
    ctx.push()
    yield client
    ctx.pop()


@pytest.fixture(scope="function")
def map_with_data(redis_map, redis_conn):
    """Fixture with pre-populated test data."""
    redis_conn.data = {'loc': {
        'R3Ea3': [24.93545, 60.16952],
        'O6zkQ': [18.0649, 59.33258]
    }}
    redis_conn.set('user:R3Ea3', '1')
    redis_conn.set('user:O6zkQ', '2')
    redis_conn.set('nick:R3Ea3', 'A A')
    redis_conn.set('nick:O6zkQ', 'B B')
    yield
    redis_conn.data = {}


@pytest.fixture(scope='function')
def redis_map(redis_conn):
    yield RedisMap(MagicMock(), redis_conn)
    redis_conn.data = {}
