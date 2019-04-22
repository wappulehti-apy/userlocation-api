import sys
import logging
import os
from flask import Flask
from flask_basicauth import BasicAuth
from flask_cors import CORS
from redismap import RedisMap
from apscheduler.schedulers.gevent import GeventScheduler


def create_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    logger.addHandler(handler)
    return logger


# from apscheduler.schedulers.background import BackgroundScheduler as GeventScheduler

bglogger = create_logger(__name__)
scheduler = GeventScheduler()
basic_auth = BasicAuth()
redis_map = RedisMap()


@scheduler.scheduled_job('interval', id='clean_redis', minutes=5)
def clean_redis():
    bglogger.info('BG: cleaning redis')
    redis_map.expire_locations()


def create_app(redis_conn=None):
    settings_class = os.getenv('APP_SETTINGS', 'config.Config')
    app = Flask(__name__)
    app.logger.setLevel(logging.DEBUG)
    app.url_map.strict_slashes = False

    from location import location
    from requestcall import requestcall
    app.register_blueprint(location)
    app.register_blueprint(requestcall)

    app.logger.info(f'APP_SETTINGS from {settings_class}')
    app.config.from_object(settings_class)
    CORS(app, origins=app.config['CORS_ORIGINS'], supports_credentials=True)

    from database import db
    db.init_app(app)
    basic_auth.init_app(app)

    if redis_conn is None:
        import redis
        app.redis = redis.from_url(app.config["REDIS_URL"], decode_responses=True)
    else:
        app.redis = redis_conn
    redis_map.init_app(app, app.redis)

    if app.config['TESTING']:
        pass
    else:
        scheduler.start()
        bglogger.info('BG: started')

    return app
