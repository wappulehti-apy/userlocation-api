import os
from flask_caching import Cache


def create_cache(app):
    # From https://devcenter.heroku.com/articles/memcachier
    cache = Cache()
    cache_servers = os.environ.get('MEMCACHIER_SERVERS')
    app.logger.info('memcachier servers: %s', cache_servers)
    if cache_servers is None:
        # Fall back to simple in memory cache (development)
        cache.init_app(app, config={'CACHE_TYPE': 'simple'})
    else:
        cache_user = os.environ.get('MEMCACHIER_USERNAME') or ''
        cache_pass = os.environ.get('MEMCACHIER_PASSWORD') or ''
        app.logger.info('username {}'.format(cache_user))
        cache.init_app(app,
                       config={'CACHE_TYPE': 'saslmemcached',
                               'CACHE_MEMCACHED_SERVERS': cache_servers.split(','),
                               'CACHE_MEMCACHED_USERNAME': cache_user,
                               'CACHE_MEMCACHED_PASSWORD': cache_pass})

    return cache
