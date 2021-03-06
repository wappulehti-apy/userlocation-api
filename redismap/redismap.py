import os
import datetime
from flask import current_app as app
from hashids import Hashids
from collections import namedtuple

hashids = Hashids(salt=os.getenv("SALT", "default"), min_length=5)
Coordinate = namedtuple('Coordinate', ['longitude', 'latitude'])
Location = namedtuple('Location', ['public_id', 'coordinate', 'nick'])


class RedisMap():
    def __init__(self, app=None, redis_conn=None):
        self.locationkey = 'loc'
        self.nickkey = 'nick'
        if app is not None or redis_conn is not None:
            self.init_app(app, redis_conn)

    def init_app(self, app, redis_conn):
        self.app = app
        self.r = redis_conn

    @staticmethod
    def get_public_id(id):
        # seems int casting is necessary
        return hashids.encode(int(id))

    def get_user_id(self, public_id):
        if not self.user_exists(public_id):
            return None
        return hashids.decode(public_id)

    def get_nick(self, public_id):
        return self.r.get(f'{self.nickkey}:{public_id}')

    def user_exists(self, public_id):
        """if nickkey:public_id exists, user exists."""
        return self.r.exists(f'{self.nickkey}:{public_id}') == 1

    def expire_locations(self):
        for key in self.r.zscan_iter(self.locationkey):
            public_id = key[0]
            # Check if user has timed out
            if not self.user_exists(public_id):
                self.app.logger.info(f'expiring user {public_id}')
                self.r.zrem(self.locationkey, public_id)

    def get_locations(self, longitude, latitude, radius=10):
        locations = self.r.georadius(self.locationkey, longitude, latitude, radius, unit='km', withcoord=True)
        locations_with_nick = [
            Location(loc[0], Coordinate(*loc[1]), self.get_nick(loc[0]))
            for loc in locations]

        # Filter out timed out users
        return list(filter(lambda l: l.nick is not None, locations_with_nick))

    def get_locations_named(self, *args, **kwargs):
        locations = self.get_locations(*args, **kwargs)
        return [Location(loc[0], Coordinate(*loc[1]), loc[2]) for loc in locations]

    def add_or_update_user(self, id, nick, public_id=None):
        expire_seconds = 60 * 15
        public_id = public_id or self.get_public_id(id)
        self.r.setex(f'{self.nickkey}:{public_id}', expire_seconds, nick)

    def update_user_location(self, id, longitude, latitude, nick):
        assert id is not None
        assert id != ''
        public_id = self.get_public_id(id)
        self.r.geoadd(self.locationkey, longitude, latitude, public_id)
        self.add_or_update_user(id, nick, public_id=public_id)

    def remove_user_location(self, id):
        assert id is not None
        assert id != ''
        public_id = self.get_public_id(id)
        self.r.zrem(self.locationkey, public_id)
        self.r.delete(f'{self.nickkey}:{public_id}')

    @staticmethod
    def to_json(location):
        return {
            'public_id': location.public_id,
            'nick': location.nick,
            'location': {
                'lon': location.coordinate.longitude,
                'lat': location.coordinate.latitude
            }
        }
