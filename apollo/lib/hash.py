import bcrypt


def hash_plaintext(plaintext: str, salt: str = bcrypt.gensalt()):
    return (bcrypt.hashpw(plaintext.encode('utf-8'), salt).decode('utf-8'),
            salt.decode('utf-8'))


def compare_plaintext_to_hash(plaintext: str, hashed_plaintext: str,
                              salt: str):
    new_hashed_plaintext = bcrypt.hashpw(plaintext.encode('utf-8'),
                                         salt.encode('utf-8'))
    if new_hashed_plaintext == hashed_plaintext.encode('utf-8'):
        return True

    return False
