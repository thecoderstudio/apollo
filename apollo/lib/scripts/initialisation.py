import string
from secrets import choice

from apollo.lib.hash import hash_plaintext
from apollo.lib.decorators import with_db_session
from apollo.models import save
from apollo.models.user import User, count_users


def random_password():
    alphabet = string.ascii_letters + string.digits
    while True:
        password = ''.join(choice(alphabet) for i in range(12))
        if (any(character.islower() for character in password)
                and any(character.isupper() for character in password)
                and sum(character.isdigit() for character in password) >= 3):
            break
    return password


def add_admin_user(session):
    password = random_password()
    password_hash, password_salt = hash_plaintext(password)

    save(session,
         User(username='admin', password_hash=password_hash,
              password_salt=password_salt))

    print("--- Welcome to apollo. ---\n\n
          + "Your admin username is 'admin'.\n"
          + f"your password is '{password}'\n")


@with_db_session
def initialise_if_needed(**kwargs):
    session = kwargs['session']
    if count_users(session) == 0:
        add_admin_user(session)
