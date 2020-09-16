from fastapi import HTTPException

from apollo.lib.redis import RedisSession


class RequestShield:
    def __init__(self, resource, max_attempts, lockout_interval,
                 max_lockout_time):
        self.resource = resource
        self.max_attempts = max_attempts
        self.lockout_interval = lockout_interval
        self.max_lockout_time = max_lockout_time
        self.redis_session = RedisSession()

    def lock_if_required(self, key):
        locked_key = self._get_locked_key(key)
        if self.redis_session.get_from_cache(locked_key, 0):
            locked_time = self.redis_session.get_ttl(locked_key)
            raise HTTPException(
                status_code=400,
                detail="This account is locked, "
                f"try again in {locked_time} seconds"
            )

    def increment_attempts(self, key):
        attempt_key = self._get_attempt_key(key)
        locked_key = self._get_locked_key(key)

        attempt = int(self.redis_session.get_from_cache(attempt_key, 0))
        attempt += 1
        self.redis_session.write_to_cache(attempt_key, attempt)

        if attempt >= self.max_attempts:
            self.redis_session.write_to_cache(locked_key, 1, min(
                self.lockout_interval * attempt,
                self.max_lockout_time
            ))

    def clear(self, key):
        self.redis_session.delete(self._get_attempt_key(key))
        self.redis_session.delete(self._get_locked_key(key))

    @staticmethod
    def _get_attempt_key(key):
        return f"attempt:{key}"

    @staticmethod
    def _get_locked_key(key):
        return f"locked:{key}"
