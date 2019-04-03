import os
from dotenv import load_dotenv

load_dotenv(verbose=True)


class Config(object):
    DEBUG = False
    CSRF_ENABLED = True
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY") or "this-really-needs-to-be-changed"
    BASIC_AUTH_USERNAME = os.getenv("BASIC_AUTH_USERNAME")
    BASIC_AUTH_USERNAME = os.getenv("BASIC_AUTH_PASSWORD")
    GEO_NAME = os.getenv("GEO_NAME") or 'default'
    API_VERSION = "1.0"
