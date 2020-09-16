import redis

from apollo.lib.singleton import Singleton


class RedisSession(object, metaclass=Singleton):
    def __init__(self, host, port, db, default_item_lifetime, password=None):
        self.session = redis.StrictRedis(host=host, port=port, db=db,
                                         password=password)
        self.default_lifetime = default_item_lifetime

    def write_to_cache(self, key, value, lifetime=None):
        if not lifetime:
            lifetime = self.default_lifetime
        self.session.set(key, value, ex=lifetime)

    def write_dict_to_cache(self, key, value):
        self.session.hmset(key, value)

    def get_dict_from_cache(self, key):
        return self.session.hgetall(key)

    def get_from_cache(self, key):
        return self.session.get(key)
