import base64
import bcrypt
import jwt

from datetime import timedelta, datetime

from apollo.lib.settings import settings

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

def create_access_token(data: dict, expires_in: timedelta):
    to_encode = data.copy()
    to_encode.update({"experation_date": datetime.utcnow() + expires_in})
    return jwt.encode(
        to_encode, settings['app']['access_token_key'], algorithm="HS256")

def decode_access_token(token: str):
    decoded = jwt.decode(token, settings['app']['access_token_key'], algorithm="HS256")
    return decoded