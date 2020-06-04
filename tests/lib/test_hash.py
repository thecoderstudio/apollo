from apollo.lib.hash import hash_plaintext, compare_plaintext_to_hash

def test_password_hash():
    password_hash, salt = hash_plaintext('password')

    assert compare_plaintext_to_hash('password', password_hash, salt) == True
    assert compare_plaintext_to_hash('fakepassword', password_hash, salt) == False

def test_hash_no_password():
    password_hash, salt = hash_plaintext('password')

    assert compare_plaintext_to_hash(None, password_hash, salt) == False

