import os


class Config(object):
    """Base config. Used in Production."""
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True

    # From ENV variables
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY") or "this-really-needs-to-be-changed"
    BASIC_AUTH_USERNAME = os.getenv("BASIC_AUTH_USERNAME")
    BASIC_AUTH_PASSWORD = os.getenv("BASIC_AUTH_PASSWORD")
    WEBHOOK_URL = os.getenv('WEBHOOK_URL')
    REDIS_URL = os.getenv("REDIS_URL")
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "").split(",")


class Develop(Config):
    from dotenv import load_dotenv
    load_dotenv(verbose=True)
    REDIS_URL = "redis://redis"


class Testing(Config):
    DEBUG = True
    TESTING = True
    SECRET_KEY = "mysecretkey"
    BASIC_AUTH_USERNAME = "myusername"
    BASIC_AUTH_PASSWORD = "mypassword"
    WEBHOOK_URL = "https://example.com/webhook"
