import pytest
from unittest.mock import patch, MagicMock
from fakeredis import FakeRedis
from app import create_app
from redismap import RedisMap


@pytest.fixture(scope='session')
def redis_conn():
    class AugmentedFakeredis(FakeRedis):
        "implements geoadd and georadius for FakeRedis"

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
    redis_conn.data = {'loc': {
        'R3Ea3': [24.93545, 60.16952],
        'O6zkQ': [18.0649, 59.33258]
    }}
    redis_conn.set('initials:R3Ea3', 'A A')
    redis_conn.set('initials:O6zkQ', 'B B')
    yield
    redis_conn.data = {}


@pytest.fixture(scope='function')
def redis_mock(redis_conn):
    return MagicMock()


@pytest.fixture(scope='function')
def redis_map(redis_conn):
    yield RedisMap(MagicMock(), redis_conn)
    redis_conn.data = {}


@pytest.fixture(scope='function')
def redis_map_mock(redis_mock):
    yield RedisMap(MagicMock(), redis_mock)
