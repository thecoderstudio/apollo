from configparser import ConfigParser

import redis

from apollo.lib.redis import RedisSession


def test_redis_session_singleton(redis_session):
    RedisSession() is redis_session


def test_write_to_cache(redis_session):
    strict_redis, lifetime = get_strict_redis()

    redis_session.write_to_cache('test', 'a')

    assert strict_redis.ttl('test') == int(lifetime)
    assert strict_redis.get('test') == b'a'


def test_write_dict_to_cache(redis_session):
    strict_redis, _ = get_strict_redis()
    data = {b'a': b'b'}

    redis_session.write_dict_to_cache('data', data)

    assert strict_redis.hgetall('data') == data


def test_get_dict_from_cache(redis_session):
    data = {b'a': b'b'}
    redis_session.write_dict_to_cache('test', data)

    assert redis_session.get_dict_from_cache('test') == data


def test_get_from_cache(redis_session):
    data = b'a'
    redis_session.write_to_cache('test', data)

    assert redis_session.get_from_cache('test') == data


def get_strict_redis():
    config = ConfigParser()
    config.read('test.ini')
    redis_settings = config['redis']
    lifetime = redis_settings.pop('default_item_lifetime')

    return redis.StrictRedis(**redis_settings), lifetime
