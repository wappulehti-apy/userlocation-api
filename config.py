import os
from dotenv import load_dotenv


class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True

    # From ENV variables
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY") or "this-really-needs-to-be-changed"
    BASIC_AUTH_USERNAME = os.getenv("BASIC_AUTH_USERNAME")
    BASIC_AUTH_PASSWORD = os.getenv("BASIC_AUTH_PASSWORD")
    GEO_NAME = os.getenv("GEO_NAME") or 'default'
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    BOT_WEBHOOK_URL = os.getenv('BOT_WEBHOOK_URL')


class Develop(Config):
    load_dotenv(verbose=True)
    SQLALCHEMY_DATABASE_URI = "postgres://postgres:@postgres/postgres"
    DEVELOP = True


class Testing(Config):
    TESTING = True
    SECRET_KEY = "mysecretley"
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    BASIC_AUTH_USERNAME = "myusername"
    BASIC_AUTH_PASSWORD = "mypassword"
    GEO_NAME = "myname"
