from fastapi import Depends, HTTPException, Response
from sqlalchemy.orm import Session

from apollo.lib.hash import compare_plaintext_to_hash
from apollo.lib.router import SecureRouter
from apollo.lib.schemas.auth import LoginSchema
from apollo.lib.security import Allow, Everyone, create_session_cookie
from apollo.lib.settings import settings
from apollo.lib.security.shield import RequestShield
from apollo.models import get_session
from apollo.models.user import get_user_by_username

router = SecureRouter([(Allow, Everyone, 'login')])

FAKE_PASSWORD_HASH = (
    "$2b$12$TEfhqmu/6mXaYqMZUkTAZuP51uAJH2qN0lPenzFtwnvcSWPKsCFyS")
FAKE_PASSWORD_SALT = "$2b$12$TEfhqmu/6mXaYqMZUkTAZu"


@router.post("/auth/login", status_code=200, permission='login')
def login(response: Response, login_data: LoginSchema,
          session: Session = Depends(get_session)):
    security_settings = settings['security']
    shield = RequestShield(
        login_data.username,
        int(security_settings['max_login_attempts']),
        int(security_settings['login_lockout_interval_in_seconds']),
        int(security_settings['max_login_lockout_in_seconds'])
    )

    user = get_user_by_username(session, login_data.username)
    shield.raise_if_locked(resource="account")
    shield.increment_attempts()

    if user:
        password_hash, password_salt = user.password_hash, user.password_salt
    else:
        # Compare given credentials with fake credentials to avoid timing
        # attacks.
        password_hash, password_salt = FAKE_PASSWORD_HASH, FAKE_PASSWORD_SALT

    if not compare_plaintext_to_hash(login_data.password, password_hash,
                                     password_salt):
        raise HTTPException(status_code=400,
                            detail="Username and/or password is incorrect")

    shield.clear()
    response.set_cookie(*create_session_cookie(user))
