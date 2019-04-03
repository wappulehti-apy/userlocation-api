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
        cache.init_app(app,
                       config={'CACHE_TYPE': 'saslmemcached',
                               'CACHE_MEMCACHED_SERVERS': cache_servers.split(','),
                               'CACHE_MEMCACHED_USERNAME': cache_user,
                               'CACHE_MEMCACHED_PASSWORD': cache_pass,
                               'CACHE_OPTIONS': {'behaviors': {
                                   # Faster IO
                                   'tcp_nodelay': True,
                                   # Keep connection alive
                                   'tcp_keepalive': True,
                                   # Timeout for set/get requests
                                   'connect_timeout': 2000,  # ms
                                   'send_timeout': 750 * 1000,  # us
                                   'receive_timeout': 750 * 1000,  # us
                                   '_poll_timeout': 2000,  # ms
                                   # Better failover
                                   'ketama': True,
                                   'remove_failed': 1,
                                   'retry_timeout': 2,
                                   'dead_timeout': 30}}})
    return cache
