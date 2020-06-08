from secrets import token_urlsafe

from apollo.lib.hash import hash_plaintext
from apollo.lib.decorators import with_db_session
from apollo.models import save
from apollo.models.user import User, count_users


def add_admin_user(session):
    password = token_urlsafe(12)
    password_hash, password_salt = hash_plaintext(password)

    save(session,
         User(username='admin', password_hash=password_hash,
              password_salt=password_salt))

    print("--- Welcome to apollo. ---\n\n"
          + "Your admin username is 'admin'.\n"
          + f"Your password is '{password}'\n")


@with_db_session
def initialise_if_needed(session):
    if count_users(session) == 0:
        add_admin_user(session)
