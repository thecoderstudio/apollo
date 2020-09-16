from configparser import ConfigParser

import redis

from apollo.lib.redis import RedisSession


def test_redis_session_singleton(redis_session):
    RedisSession() is redis_session


def test_redis_session_configure():
    redis_settings, lifetime = get_redis_settings()

    try:
        redis_session = RedisSession(lifetime)
        redis_session.configure(**redis_settings)

        assert redis_session.session is not None
    finally:
        redis_session.session = None


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
    data = 'a'
    redis_session.write_to_cache('test', data)

    assert redis_session.get_from_cache('test') == data


def test_get_from_cache_not_found(redis_session):
    assert redis_session.get_from_cache('fake', 'test') == 'test'


def test_get_ttl(redis_session):
    redis_session.write_to_cache('test', 'a', 10)
    assert redis_session.get_ttl('test') == 10


def test_get_ttl_not_found(redis_session):
    redis_session.get_ttl('test') is None


def test_delete(redis_session):
    redis_session.write_to_cache('test', 'a')
    redis_session.delete('test')
    assert redis_session.get_from_cache('test') is None


def test_delete_not_found(redis_session):
    redis_session.delete('test')


def get_strict_redis():
    redis_settings, lifetime = get_redis_settings()

    return redis.StrictRedis(**redis_settings), lifetime


def get_redis_settings():
    config = ConfigParser()
    config.read('test.ini')
    redis_settings = config['redis']
    lifetime = redis_settings.pop('default_ttl_in_seconds')
    return redis_settings, lifetime
