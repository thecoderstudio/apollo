import logging
import random
import string
import uuid

from configparser import ConfigParser

from apollo.lib.hash import hash_plaintext
from apollo.models import save, init_sqlalchemy
from apollo.models.user import User
from apollo import read_settings_files
from apollo.lib.settings import settings, update_settings


def randompassword():
    chars = string.ascii_uppercase + string.ascii_lowercase + string.digits
    size = random.randint(8, 12)
    return ''.join(random.choice(chars) for x in range(size))


config = ConfigParser()
config.read('../../../local-settings.ini')
update_settings(config)
init_sqlalchemy()

password = randompassword()
password_hash, password_salt = hash_plaintext(password)
user = User(id=uuid.uuid4(), username='admin',
            password_hash=password_hash, password_salt=password_salt)
save(user)

print(f'Your admin username is: admin, and your password is: {password}')
