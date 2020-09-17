from fastapi import HTTPException

from apollo.lib.redis import RedisSession

BIGGER_THAN_0_ERROR = "{} needs to be bigger than 0"


class RequestShield:
    def __init__(
        self,
        key: str,
        max_attempts: int,
        lockout_interval_in_seconds: int,
        max_lockout_time_in_seconds: int
    ):
        if max_attempts < 0:
            raise ValueError("max_attempts can't be negative")
        elif lockout_interval_in_seconds < 1:
            raise ValueError(BIGGER_THAN_0_ERROR.format(
                "lockout_interval_in_seconds"))
        elif max_lockout_time_in_seconds < 1:
            raise ValueError(BIGGER_THAN_0_ERROR.format(
                "max_lockout_time_in_seconds"))

        self.max_attempts = max_attempts
        self.lockout_interval = lockout_interval_in_seconds
        self.max_lockout_time = max_lockout_time_in_seconds
        self.redis_session = RedisSession()

        self.attempt_key = f"attempt:{key}"
        self.locked_key = f"locked:{key}"

    def raise_if_locked(self, resource: str = "resource"):
        if self.locked:
            raise HTTPException(
                status_code=400,
                detail=f"This {resource} is locked, "
                f"try again in {self.time_locked_in_seconds} seconds"
            )

    def increment_attempts(self):
        if self.locked:
            raise ValueError("Can't reattempt when locked")

        attempt = int(self.redis_session.get_from_cache(self.attempt_key, 0))
        attempt += 1
        self.redis_session.write_to_cache(self.attempt_key, attempt)

        if attempt > self.max_attempts:
            self.redis_session.write_to_cache(self.locked_key, 1, min(
                self.lockout_interval * attempt,
                self.max_lockout_time
            ))

    def clear(self):
        self.redis_session.delete(self.attempt_key)
        self.redis_session.delete(self.locked_key)

    @property
    def attempts(self) -> int:
        return int(self.redis_session.get_from_cache(self.attempt_key, 0))

    @property
    def locked(self) -> bool:
        return bool(self.redis_session.get_from_cache(
            self.locked_key
        ))

    @property
    def time_locked_in_seconds(self) -> int:
        return self.redis_session.get_ttl(self.locked_key)
