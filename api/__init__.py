import sys
import os
import logging
from flask import Flask
from flask_cors import CORS
from flask_restful import Resource
from redismap import redis_map
from api.auth import basic_auth
from webhook import webhook
from bg import bg_jobs


def is_main_workzeug_process():
    # Workzeug (dev server) spawns also a child process
    return os.getenv('WERKZEUG_RUN_MAIN') == 'true'


def create_app(redis_conn=None):
    settings_class = os.getenv('APP_SETTINGS', 'config.Config')

    app = Flask(__name__)
    app.config.from_object(settings_class)
    CORS(app, origins=app.config['CORS_ORIGINS'], supports_credentials=True)

    # Redis
    if redis_conn is None:
        import redis
        app.redis = redis.from_url(app.config["REDIS_URL"], decode_responses=True)
    else:
        app.redis = redis_conn
    redis_map.init_app(app, app.redis)

    # Api
    from api import routes
    routes.init_app(app)
    basic_auth.init_app(app)
    app.logger.setLevel(logging.DEBUG)
    # app.url_map.strict_slashes = False

    # Webhook
    webhook.init_app(app, app.config['WEBHOOK_URL'])

    # Environment specific
    if settings_class == 'config.Config':
        from apscheduler.schedulers.gevent import GeventScheduler as Scheduler
        bg_jobs.init_app(app, Scheduler)
    elif settings_class == 'config.Develop':
        from api import localtest
        app.register_blueprint(localtest.bp)

        if is_main_workzeug_process():
            from apscheduler.schedulers.background import BackgroundScheduler as Scheduler
            bg_jobs.init_app(app, Scheduler)
    elif settings_class == 'config.Testing':
        pass
    else:
        raise Exception(f'Unknown settings_class: {settings_class}')

    app.logger.info(f'Loaded {settings_class} configuration')

    return app
