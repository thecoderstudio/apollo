from fastapi import APIRouter, Depends

from apollo.lib.encrypt import hash_plaintext, get_user_from_access_token
from apollo.lib.schemas.user import UserInSchema, UserOutSchema
from apollo.handlers import save
from apollo.models.user import User

router = APIRouter()


@router.post('/user')
async def post_user(result: UserInSchema, current_user=Depends(get_user_from_access_token)):
    data = result.dict()
    data['password_hash'], data['password_salt'] = hash_plaintext(
        result.password)
    data.pop('password')

    user = save(User(**data))
    return UserOutSchema.from_orm(user)
