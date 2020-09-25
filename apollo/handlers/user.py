import uuid
from typing import List

from fastapi import Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from apollo.lib.exceptions import HTTPException
from apollo.lib.hash import hash_plaintext, compare_plaintext_to_hash
from apollo.lib.router import SecureRouter
from apollo.lib.schemas.user import (
    CreateUserSchema, UserSchema, UpdateUserSchema)
from apollo.lib.security import (Allow, Admin, Human, Authenticated,
                                 Uninitialized)
from apollo.models import get_session, save, delete
from apollo.models.user import User, get_user_by_id, list_users as query_users

router = SecureRouter([
    (Allow, Admin, 'user.post'),
    (Allow, Admin, 'user.delete'),
    (Allow, Admin, 'user.list'),
    (Allow, Human, 'user.get_current'),
    (Allow, Human, 'user.patch_self'),
    (Allow, Uninitialized, 'user.patch_self')
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


@router.patch('/user/me', status_code=200,
              response_model=UserSchema, permission='user.patch_self')
def patch_user(user_data: UpdateUserSchema, request: Request,
               session: Session = Depends(get_session)):
    user = request.current_user
    data = user_data.dict()

    if not compare_plaintext_to_hash(user_data.old_password,
                                     user.password_hash,
                                     user.password_salt):
        return JSONResponse(
            status_code=400,
            content={
                'old_password': {
                    'msg': 'Invalid password',
                    'type': 'value_error'
                }
            }
        )

    data['password_hash'], data['password_salt'] = hash_plaintext(
        user_data.pop('password'))
    user.has_changed_initial_password = True

    user.set_fields(data)
    saved_user, _ = save(session, user)
    return saved_user


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


@router.get('/user/me', permission='user.get_current',
            response_model=UserSchema)
def get_current_user(request: Request):
    return request.current_user
