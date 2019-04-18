import os
import datetime
from flask import current_app as app
from hashids import Hashids

hashids = Hashids(salt=os.getenv("SALT", "default"), min_length=5)

# def generate_public_id(id):
#     return hashids.encode(id)


class RedisMap():
    def __init__(self, app=None, redis_conn=None):
        self.locationkey = 'loc'
        self.userkey = 'user'
        if app is not None or redis_conn is not None:
            self.init_app(app, redis_conn)

    def init_app(self, app, redis_conn):
        self.app = app
        self.r = redis_conn

    def _get_public_id(self, id):
        return hashids.encode(id)

    def expire_locations(self):
        for key in self.r.zscan_iter(self.locationkey):
            public_id = key[0]
            # Check if user has timed out
            if not self.r.exists(f'{self.userkey}:{public_id}'):
                self.app.logger.info(f'expiring user {public_id}')
                self.r.zrem(self.locationkey, public_id)

    def get_locations(self, longitude, latitude, radius=10):
        users = self.r.georadius(self.locationkey, longitude, latitude, radius, unit='km', withcoord=True)
        self.expire_locations()
        return users

    def add_or_update_user(self, id, initials=None, public_id=None):
        expire_seconds = 60 * 5
        public_id = public_id or self._get_public_id(id)
        self.r.setex(f'user:{public_id}', expire_seconds, str(id))
        # TODO exception handling

    def update_user_location(self, id, longitude, latitude, initials):
        public_id = self._get_public_id(id)
        self.r.geoadd(self.locationkey, longitude, latitude, public_id)
        self.add_or_update_user(id, initials=initials, public_id=public_id)
        # TODO exception handling

    @staticmethod
    def to_json(location):
        return {
            'id': location[0],
            'longitude': location[1][0],
            'latitude': location[1][1]
        }
