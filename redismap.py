import os
import datetime
from flask import current_app as app
from hashids import Hashids

hashids = Hashids(salt=os.getenv("SALT", "default"), min_length=5)

# def generate_public_id(id):
#     return hashids.encode(id)


class RedisMap():
    def __init__(self, redis_conn):
        self.locationkey = 'loc'
        self.userkey = 'user'
        self.r = redis_conn

    def _get_public_id(self, id):
        return hashids.encode(id)

    def expire_locations(self):
        # for key in self.r.zscan_iter(f'{self.userkey}:*'):
        try:
            for key in self.r.zscan_iter(self.locationkey):
                app.logger.error(key)
        except TypeError as err:
            app.logger.error(err)
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
