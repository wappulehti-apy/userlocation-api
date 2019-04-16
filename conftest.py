import pytest
import fakeredis
from app import create_app
from database import db


@pytest.fixture(scope='session')
def redis_conn():
    return fakeredis.FakeStrictRedis()


@pytest.fixture(scope='session')
def app(redis_conn):
    _app = create_app(redis_conn=redis_conn)
    yield _app


@pytest.fixture(scope='session')
def client(app):
    client = app.test_client()

    # Establish an application context before running the tests.
    ctx = app.app_context()
    ctx.push()
    yield client
    ctx.pop()


@pytest.fixture(scope='session')
def database():
    db.create_all()
    return db


@pytest.fixture(scope='session')
def _db(database):
    """Required by pytest-flask-sqlalchemy"""
    return database
