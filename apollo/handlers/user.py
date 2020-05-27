from apollo.handlers import router

@router.post('/user')
def post_user():
    return