from fastapi import HTTPException

from apollo.lib.redis import RedisSession


class RequestShield:
    def __init__(self, resource, key, max_attempts, lockout_interval,
                 max_lockout_time):
        self.resource = resource
        self.max_attempts = max_attempts
        self.lockout_interval = lockout_interval
        self.max_lockout_time = max_lockout_time
        self.redis_session = RedisSession()

        self.attempt_key = f"attempt:{key}"
        self.locked_key = f"locked:{key}"

    def raise_if_locked(self):
        if self.locked:
            raise HTTPException(
                status_code=400,
                detail="This account is locked, "
                f"try again in {self.time_locked_in_seconds} seconds"
            )

    def increment_attempts(self):
        attempt = int(self.redis_session.get_from_cache(self.attempt_key, 0))
        attempt += 1
        self.redis_session.write_to_cache(self.attempt_key, attempt)

        if attempt >= self.max_attempts:
            self.redis_session.write_to_cache(self.locked_key, 1, min(
                self.lockout_interval * attempt,
                self.max_lockout_time
            ))

    def clear(self):
        self.redis_session.delete(self.attempt_key)
        self.redis_session.delete(self.locked_key)

    @property
    def attempts(self):
        return int(self.redis_session.get_from_cache(self.attempt_key, 0))

    @property
    def locked(self):
        return bool(self.redis_session.get_from_cache(
            self.locked_key
        ))

    @property
    def time_locked_in_seconds(self):
        return self.redis_session.get_ttl(self.locked_key)
