from apollo.lib.hash import hash_plaintext, compare_plaintext_to_hash

def test_password_hash():
    password_hash, password_salt = hash_plaintext('password')

    assert compare_plaintext_to_hash('password', password_hash, password_salt) == True
    assert compare_plaintext_to_hash('fakepassword', password_hash, password_salt) == False

def test_password_hash_no_salt():
    password_hash, _ = hash_plaintext('password')

    assert compare_plaintext_to_hash('password', password_hash) == False

def test_hash_no_password():
    password_hash, _ = hash_plaintext('password')

    assert compare_plaintext_to_hash(None, password_hash) == False

