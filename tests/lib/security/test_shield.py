import time

import pytest
from fastapi import HTTPException

from apollo.lib.security.shield import RequestShield


def test_lock_on_too_many_attempts():
    shield = RequestShield('test', 3, 5, 15)

    shield.increment_attempts()
    assert shield.attempts == 1
    assert shield.locked is False

    shield.increment_attempts()
    assert shield.attempts == 2
    assert shield.locked is False

    shield.increment_attempts()
    assert shield.attempts == 3
    assert shield.locked is True
    assert shield.time_locked_in_seconds == 15


def test_no_reattempt_when_locked():
    shield = RequestShield('test', 1, 10, 15)
    shield.increment_attempts()

    with pytest.raises(ValueError, match="Can't reattempt when locked"):
        shield.increment_attempts()


def test_raise_when_locked():
    shield = RequestShield('test', 1, 5, 15)
    shield.increment_attempts()

    with pytest.raises(HTTPException) as e:
        shield.raise_if_locked()
        print(str(e))


def test_no_raise_when_not_locked():
    shield = RequestShield('test', 1, 5, 15)
    shield.raise_if_locked()


def test_locktime_increases_with_every_failed_attempt():
    shield = RequestShield('test', 1, 1, 15)
    shield.increment_attempts()

    time.sleep(2)

    shield.increment_attempts()

    assert shield.time_locked_in_seconds == 2


def test_locktime_does_not_exceed_maximum():
    shield = RequestShield('test', 1, 10, 5)
    shield.increment_attempts()

    assert shield.time_locked_in_seconds == 5


def test_clear():
    shield = RequestShield('test', 1, 10, 5)
    shield.increment_attempts()

    shield.clear()
    assert shield.attempts == 0
    assert shield.locked is False
