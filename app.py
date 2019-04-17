
import os
from flask import Flask
from flask_basicauth import BasicAuth
from flask_migrate import Migrate
import logging


migrate = Migrate()
basic_auth = BasicAuth()


def create_app(redis_conn=None):
    settings_class = os.getenv('APP_SETTINGS', 'config.Config')
    app = Flask(__name__)
    app.url_map.strict_slashes = False

    from location import location
    from requestcall import requestcall
    app.register_blueprint(location)
    app.register_blueprint(requestcall)

    app.logger.info(f'APP_SETTINGS from {settings_class}')
    app.config.from_object(settings_class)

    app.logger.setLevel(logging.DEBUG)

    from database import db
    db.init_app(app)
    migrate.init_app(app, db)
    basic_auth.init_app(app)

    if redis_conn is None:
        import redis
        app.redis = redis.from_url(app.config["REDIS_URL"], decode_responses=True)
    else:
        app.redis = redis_conn

    return app
