import bmemcached
import os


def create_cache(app):

    servers = os.environ.get('MEMCACHIER_SERVERS', '').split(',')
    user = os.environ.get('MEMCACHIER_USERNAME', '')
    passw = os.environ.get('MEMCACHIER_PASSWORD', '')
    if servers is None:
        from flask_caching import Cache
        cache = Cache() 
        # Fall back to simple in memory cache (development)
        cache.init_app(app, config={'CACHE_TYPE': 'simple'})
        return cache

    cache = bmemcached.Client(servers, username=user, password=passw)

    cache.enable_retry_delay(True)  # Enabled by default. Sets retry delay to 5s.
    return cache
