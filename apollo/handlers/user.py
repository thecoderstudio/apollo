from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from apollo.lib.hash import hash_plaintext
from apollo.lib.schemas.user import CreateUserSchema, UserSchema
from apollo.models import get_session, save
from apollo.models.user import User

router = APIRouter()


@router.post('/user', status_code=201, response_model=UserSchema)
def post_user(user_data: CreateUserSchema,
              session: Session = Depends(get_session)):
    data = user_data.dict()
    data['password_hash'], data['password_salt'] = hash_plaintext(
        user_data.password)
    data.pop('password')

    user, _ = save(session, User(**data))
    return user
