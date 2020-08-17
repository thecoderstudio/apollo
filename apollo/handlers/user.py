from typing import List

from fastapi import Depends
from sqlalchemy.orm import Session

from apollo.lib.hash import hash_plaintext
from apollo.lib.router import SecureRouter
from apollo.lib.schemas.user import CreateUserSchema, UserSchema
from apollo.lib.security import Allow
from apollo.models import get_session, save
from apollo.models.user import User, list_users as query_users

router = SecureRouter([(Allow, 'role:admin', 'user.post')])


@router.post('/user', status_code=201, response_model=UserSchema,
             permission='user.post')
def post_user(user_data: CreateUserSchema,
              session: Session = Depends(get_session)):
    data = user_data.dict()
    data['password_hash'], data['password_salt'] = hash_plaintext(
        user_data.password)
    data.pop('password')

    user, _ = save(session, User(**data))
    return user


@router.get('/user', status_code=200, response_model=List[UserSchema],
            permission='user.list')
def list_users(session: Session = Depends(get_session)):
    return query_users(session)
