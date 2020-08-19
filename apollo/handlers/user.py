import uuid
from typing import List

from fastapi import Depends
from sqlalchemy.orm import Session

from apollo.lib.exceptions import HTTPException
from apollo.lib.hash import hash_plaintext
from apollo.lib.router import SecureRouter
from apollo.lib.schemas.user import CreateUserSchema, UserSchema
from apollo.lib.security import Allow, ADMIN_PRINCIPAL
from apollo.models import get_session, save, delete
from apollo.models.user import User, get_user_by_id, list_users as query_users

router = SecureRouter([
    (Allow, ADMIN_PRINCIPAL, 'user.post'),
    (Allow, ADMIN_PRINCIPAL, 'user.delete'),
    (Allow, ADMIN_PRINCIPAL, 'user.list')
])


@router.post('/user', status_code=201, response_model=UserSchema,
             permission='user.post')
def post_user(user_data: CreateUserSchema,
              session: Session = Depends(get_session)):
    data = user_data.dict()
    data['password_hash'], data['password_salt'] = hash_plaintext(
        user_data.password)
    data.pop('password')

    user, _ = save(session, User(**data))
    return get_user_by_id(session, user.id)


@router.delete('/user/{user_id}', status_code=204, permission='user.delete')
def delete_user(user_id: uuid.UUID, session: Session = Depends(get_session)):
    user = get_user_by_id(session, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    elif user.role and user.role.name == 'admin':
        raise HTTPException(status_code=400,
                            detail="Can't delete other admins")
    delete(session, user)

@router.get('/user', status_code=200, response_model=List[UserSchema],
            permission='user.list')
def list_users(session: Session = Depends(get_session)):
    return query_users(session)
