import redis

from apollo.lib.settings import settings
from apollo.lib.singleton import Singleton


class RedisSession(object, metaclass=Singleton):
    def __init__(self, host, port, db, password):
        self.session = redis.StrictRedis(host=host, port=port, db=db,
                                         password=password)

    def write_to_cache(self, key, value, lifetime=None):
        if not lifetime:
            lifetime = settings['redis.default_item_lifetime']
        self.session.set(key, value, ex=lifetime)

    def write_dict_to_cache(self, key, value):
        self.session.hmset(key, value)

    def get_dict_from_cache(self, key):
        return self.session.hgetall(key)

    def get_from_cache(self, key):
        return self.session.get(key)
