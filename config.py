import os
from dotenv import load_dotenv


class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    BASIC_AUTH_FORCE = True

    # From ENV variables
    load_dotenv(verbose=True)
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY") or "this-really-needs-to-be-changed"
    BASIC_AUTH_USERNAME = os.getenv("BASIC_AUTH_USERNAME")
    BASIC_AUTH_PASSWORD = os.getenv("BASIC_AUTH_PASSWORD")
    GEO_NAME = os.getenv("GEO_NAME") or 'default'


class Testing(Config):
    TESTING = True
    SECRET_KEY = "mysecretley"
    BASIC_AUTH_USERNAME = "myusername"
    BASIC_AUTH_PASSWORD = "mypassword"
    GEO_NAME = "myname"
