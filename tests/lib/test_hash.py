from apollo.lib.hash import hash_plaintext, compare_plaintext_to_hash

def test_password_hash():
    password_hash, password_salt = hash_plaintext('password')

    assert compare_plaintext_to_hash('password', password_hash, password_salt) == True
    assert compare_plaintext_to_hash('fakepassword', password_hash, password_salt) == False


