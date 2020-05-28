from fastapi import APIRouter

from apollo.lib.hash import hash_plaintext
from apollo.lib.schemas.user import UserSchema
from apollo.handlers import save
from apollo.models.user import User, list_users

router = APIRouter()

@router.post('/user')
async def post_user(result: UserSchema):
    data = result.dict() 
    data['password_hash'], data['password_salt'] = hash_plaintext(
        result.password)
    data.pop('password')
    
    user = save(User(**data))
    user = UserSchema.from_orm(user)
    return user
