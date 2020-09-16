from fastapi import Depends, HTTPException, Response
from sqlalchemy.orm import Session

from apollo.lib.hash import compare_plaintext_to_hash
from apollo.lib.redis import RedisSession
from apollo.lib.router import SecureRouter
from apollo.lib.schemas.auth import LoginSchema
from apollo.lib.security import Allow, Everyone, create_session_cookie
from apollo.models import get_session
from apollo.models.user import get_user_by_username

router = SecureRouter([(Allow, Everyone, 'login')])

FAKE_PASSWORD_HASH = (
    "$2b$12$TEfhqmu/6mXaYqMZUkTAZuP51uAJH2qN0lPenzFtwnvcSWPKsCFyS")
FAKE_PASSWORD_SALT = "$2b$12$TEfhqmu/6mXaYqMZUkTAZu"


@router.post("/auth/login", status_code=200, permission='login')
def login(response: Response, login_data: LoginSchema,
          session: Session = Depends(get_session)):
    redis_session = RedisSession()
    attempt_key = f"login_attempt:{login_data.username}"
    locked_key = f"locked:{login_data.username}"

    if redis_session.get_from_cache(locked_key, 0):
        locked_time = redis_session.get_ttl(locked_key)
        raise HTTPException(
            status_code=400,
            detail="This account is locked, "
            f"try again in {locked_time} seconds"
        )

    user = get_user_by_username(session, login_data.username)

    if user:
        password_hash, password_salt = user.password_hash, user.password_salt
    else:
        # Compare given credentials with fake credentials to avoid timing
        # attacks.
        password_hash, password_salt = FAKE_PASSWORD_HASH, FAKE_PASSWORD_SALT

    if not compare_plaintext_to_hash(login_data.password, password_hash,
                                     password_salt):
        login_attempt = int(redis_session.get_from_cache(attempt_key, 0))
        login_attempt += 1
        redis_session.write_to_cache(attempt_key, login_attempt)

        if login_attempt >= 3:
            redis_session.write_to_cache(
                locked_key,
                1,
                min(300 * login_attempt, 10800)
            )

        raise HTTPException(status_code=400,
                            detail="Username and/or password is incorrect")

    redis_session.delete(attempt_key)
    response.set_cookie(*create_session_cookie(user))
