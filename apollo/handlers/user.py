from fastapi import APIRouter, Depends

from apollo.lib.encrypt import hash_plaintext, decode_access_token
from apollo.lib.schemas.user import UserSchema
from apollo.handlers import save
from apollo.models.user import User

router = APIRouter()

from fastapi.security import OAuth2PasswordBearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")


def get_current_user_with_token(token: str = Depends(oauth2_scheme)):
    decode = decode_access_token(token)
    print(decode)
    print("***" * 100)
    return decode

@router.post('/user')
async def post_user(result: UserSchema, current_user = Depends(get_current_user_with_token)):
    data = result.dict() 
    data['password_hash'], data['password_salt'] = hash_plaintext(
        result.password)
    data.pop('password')
    
    user = save(User(**data))
    return UserSchema.from_orm(user)
