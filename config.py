import os
from dotenv import load_dotenv

load_dotenv(verbose=True)


class Config(object):
    DEBUG = False
    CSRF_ENABLED = True
    SECRET_KEY = 'this-really-needs-to-be-changed'
    BASIC_AUTH_USERNAME = os.getenv("BASIC_AUTH_USERNAME")
    BASIC_AUTH_USERNAME = os.getenv("BASIC_AUTH_PASSWORD")
    API_VERSION = '1.0'
