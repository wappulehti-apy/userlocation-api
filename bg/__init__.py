from redismap import redis_map
from redis.exceptions import ConnectionError


def expire_users(logger):
    """Job for removing expired users' locations from redis."""
    logger.info('expiring old users')
    try:
        redis_map.expire_locations()
    except ConnectionError:
        logger.error('expire_users failed, could not connect to redis')


class BgJobs:
    def init_app(self, app, Scheduler):
        self.app = app
        self.scheduler = Scheduler()

        self.scheduler.add_job(expire_users, 'interval', minutes=30, args=[app.logger], id='expire_users', replace_existing=True)
        self.scheduler.start()


bg_jobs = BgJobs()
