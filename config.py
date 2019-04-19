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
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WEBHOOK_URL = os.getenv('WEBHOOK_URL')
    REDIS_URL = os.getenv("REDIS_URL")
    CORS_ORIGINS = [
        'https://apy.fi',
        'https://www.apy.fi'
        'https://osta.apy.fi',
        'https://xn--py-uia.fi',
        'https://www.xn--py-uia.fi',
        'https://osta.xn--py-uia.fi',
    ]


class Develop(Config):
    load_dotenv(verbose=True)
    SQLALCHEMY_DATABASE_URI = "postgres://postgres:@postgres/postgres"
    REDIS_URL = "redis://redis"
    DEVELOP = True


class Testing(Config):
    TESTING = True
    SECRET_KEY = "mysecretley"
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    BASIC_AUTH_USERNAME = "myusername"
    BASIC_AUTH_PASSWORD = "mypassword"
    GEO_NAME = "myname"
