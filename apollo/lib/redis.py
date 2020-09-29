import redis

from apollo.lib.singleton import Singleton


class RedisSession(object, metaclass=Singleton):
    def __init__(self, default_ttl_in_seconds):
        self.default_ttl_in_seconds = default_ttl_in_seconds

    def configure(self, host, port, db, password=None):
        self.session = redis.StrictRedis(host=host, port=port, db=db,
                                         password=password)

    def write_to_cache(self, key, value, ttl_in_seconds=None):
        if not ttl_in_seconds:
            ttl_in_seconds = self.default_ttl_in_seconds
        self.session.set(key, value, ex=ttl_in_seconds)

    def write_dict_to_cache(self, key, value):
        self.session.hset(key, mapping=value)

    def get_dict_from_cache(self, key):
        return self.session.hgetall(key)

    def get_from_cache(self, key, default=None):
        result = self.session.get(key)
        if result is None:
            return default
        return result.decode('utf-8')

    def get_ttl(self, key):
        ttl = self.session.ttl(key)
        if ttl < 0:
            return None

        return ttl

    def delete(self, key):
        self.session.delete(key)
