from apollo.handlers import router
from apollo.lib.decorator import request_validation
from apollo.lib.schemas.user import UserSchema

@request_validation(UserSchema)
@router.post('/user')
def post_user(result):
    print(result)
    return