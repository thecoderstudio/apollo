from fastapi import Depends, HTTPException, Response
from sqlalchemy.orm import Session

from apollo.lib.hash import compare_plaintext_to_hash
from apollo.lib.router import SecureRouter
from apollo.lib.schemas.auth import LoginSchema
from apollo.lib.security import Allow, Everyone, create_session_cookie
from apollo.models import get_session
from apollo.models.user import get_user_by_username

router = SecureRouter([(Allow, Everyone, 'login')])


@router.post("/auth/login", status_code=200, permission='login')
def login(response: Response, login_data: LoginSchema,
          session: Session = Depends(get_session)):
    user = get_user_by_username(session, login_data.username)
    if not compare_plaintext_to_hash(login_data.password, user.password_hash,
                                     user.password_salt):
        raise HTTPException(status_code=400,
                            detail="Username and/or password is incorrect")

    response.set_cookie(*create_session_cookie(user))
