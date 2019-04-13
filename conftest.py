import pytest
from app import app
from database import db


# @pytest.fixture
@pytest.fixture(scope='session')
def client(database):
    client = app.test_client()

    # Establish an application context before running the tests.
    ctx = app.app_context()
    ctx.push()
    yield client

    ctx.pop()


@pytest.fixture(scope='session')
def database():
    with app.app_context():
        db.create_all()
    return db


@pytest.fixture(scope='session')
def _db(database):
    """Required by pytest-flask-sqlalchemy"""
    return database
