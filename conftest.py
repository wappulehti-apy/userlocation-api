import pytest
from math import sqrt
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
            # naive radius check
            if sqrt((24 - longitude) ** 2 + (60 - latitude) ** 2) > radius:
                return []

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
    with patch('redismap.redismap.Hashids.encode', side_effect=FakeHashids.encode),\
            patch('redismap.redismap.Hashids.decode', side_effect=FakeHashids.decode):
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
        'hashof1': [24.93545, 60.16952],
        'hashof2': [18.0649, 59.33258]
    }}
    redis_conn.set('nick:hashof1', 'Abe')
    redis_conn.set('nick:hashof2', 'Bob')
    yield
    redis_conn.data = {}


class FakeHashids:
    """Simple hashes for testing."""
    @staticmethod
    def encode(id):
        """123 -> hashof123"""
        assert isinstance(id, int)
        return 'hashof' + str(id)

    @staticmethod
    def decode(hash):
        """hashof123 -> 123"""
        assert isinstance(hash, str)
        return int(hash[6:])

# Replace Hashids in all tests with FakeHashids
@pytest.fixture(scope='session', autouse=True)
def fake_hashids():
    with patch('redismap.redismap.Hashids.encode', side_effect=FakeHashids.encode),\
            patch('redismap.redismap.Hashids.decode', side_effect=FakeHashids.decode):
        yield


@pytest.fixture(scope='function')
def redis_map(redis_conn):
    yield RedisMap(MagicMock(), redis_conn)
    redis_conn.data = {}


@pytest.fixture(scope='function')
def redis_mock(redis_conn):
    """A dummy redis connection"""
    return MagicMock()


@pytest.fixture(scope='function')
def redis_map_mock(redis_mock):
    """RedisMap with dummy app and redis connection"""
    yield RedisMap(MagicMock(), redis_mock)
