from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from apollo.lib.encrypt import hash_plaintext, get_user_from_access_token
from apollo.lib.schemas.user import UserInSchema, UserOutSchema
from apollo.models import get_session, save
from apollo.models.user import User

router = APIRouter()


@router.post('/user')
async def post_user(user_data: UserInSchema, session: Session = Depends(get_session)):
    data = user_data.dict()
    data['password_hash'], data['password_salt'] = hash_plaintext(
        user_data.password)
    data.pop('password')

    user = save(session, User(**data))
    return UserOutSchema.from_orm(user)
