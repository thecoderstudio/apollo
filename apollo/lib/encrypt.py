import bcrypt
import jwt
from datetime import timedelta, datetime

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm.exc import NoResultFound

from apollo.lib.settings import settings
from apollo.lib.exceptions import invalid_credentials_exception
from apollo.models.user import get_user_by_id

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")


def hash_plaintext(plaintext: str):
    salt = bcrypt.gensalt()
    return (bcrypt.hashpw(plaintext.encode('utf-8'), salt).decode('utf-8'),
            salt.decode('utf-8'))


def compare_plaintext_to_hash(plaintext: str, hashed_plaintext: str = None, salt: str =None):
    if not salt:
        salt = bcrypt.gensalt().decode('utf-8')

    new_hashed_plaintext = bcrypt.hashpw(plaintext.encode('utf-8'),
                                         salt.encode('utf-8'))

    try:
        if new_hashed_plaintext == hashed_plaintext.encode('utf-8'):
            return True
    except AttributeError:
        # hashed_plaintext not given, should return False
        pass

    return False
