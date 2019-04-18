import os
import datetime
from flask import current_app as app
from hashids import Hashids

hashids = Hashids(salt=os.getenv("SALT", "default"), min_length=5)

# def generate_public_id(id):
#     return hashids.encode(id)


class SQLite3(object):

    def init_app(self, app):
        app.config.setdefault('SQLITE3_DATABASE', ':memory:')
        app.teardown_appcontext(self.teardown)

    def connect(self):
        return sqlite3.connect(current_app.config['SQLITE3_DATABASE'])

    def teardown(self, exception):
        ctx = _app_ctx_stack.top
        if hasattr(ctx, 'sqlite3_db'):
            ctx.sqlite3_db.close()

    @property
    def connection(self):
        ctx = _app_ctx_stack.top
        if ctx is not None:
            if not hasattr(ctx, 'sqlite3_db'):
                ctx.sqlite3_db = self.connect()
            return ctx.sqlite3_db


class RedisMap():
    def __init__(self, app=None, redis_conn=None):
        self.locationkey = 'loc'
        self.userkey = 'user'
        if app is not None:
            self.init_app(app, redis_conn)

    def init_app(self, app, redis_conn):
        self.app = app
        self.r = redis_conn

    def _get_public_id(self, id):
        return hashids.encode(id)

    def expire_locations(self):
        # for key in self.r.zscan_iter(f'{self.userkey}:*'):
        try:
            for key in self.r.zscan_iter(self.locationkey):
                self.app.logger.info(key)
        except TypeError as err:
            self.app.logger.error(err)
            # Get user
            # If no user
            # r.delete(key)
            # pass

    def get_locations(self, longitude, latitude, radius=10):
        users = self.r.georadius('loc', longitude, latitude, radius, unit='km', withdist=True, withcoord=True)
        # code to public id's
        return users

    def add_or_update_user(self, id, public_id=None):
        expire_seconds = 60 * 5
        public_id = public_id or self._get_public_id(id)
        self.r.setex(f'user:{id}', expire_seconds, public_id)

    def update_user_location(self, id, longitude, latitude):
        public_id = self._get_public_id(id)
        self.r.geoadd(self.locationkey, longitude, latitude, str(id))
        self.add_or_update_user(id, public_id=public_id)
