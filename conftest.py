import pytest
import fakeredis
from app import create_app
from database import db


@pytest.fixture(scope='session')
def redis_conn():
    return fakeredis.FakeStrictRedis(decode_responses=True)


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


@pytest.fixture(scope="function")
def db_with_data(db_session):
    from models import Location
    location1 = Location(1, latitude=60.16952, longitude=24.93545, initials="A A")
    location2 = Location(2, latitude=59.33258, longitude=18.0649, initials="B B")
    db_session.add(location1)
    db_session.add(location2)
    db_session.commit()

    yield

    # Automatically rolled back by pytest-flask-sqlalchemy
