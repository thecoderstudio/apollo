import pytest

from apollo.lib.hash import hash_plaintext, compare_plaintext_to_hash


def test_hash_plaintext():
    password_hash, _ = hash_plaintext(
        'password', '$2b$12$50eN8MSIm9KDRpzmGL4JQO'.encode('utf-8'))

    assert password_hash == (
        '$2b$12$50eN8MSIm9KDRpzmGL4JQO9gGy.2MDAafSOtqu9mZwfkb7jh33j26')

    password_hash, _ = hash_plaintext('password')

    assert password_hash != (
        '$2b$12$50eN8MSIm9KDRpzmGL4JQO9gGy.2MDAafSOtqu9mZwfkb7jh33j26')


def test_hash_plaintext_no_salt_different_outcome():
    password_hash, _ = hash_plaintext('password')
    password_hash_2, _ = hash_plaintext('password')

    assert  password_hash != password_hash_2


def test_compare_plaintext_to_hash():
    password_hash = (
        '$2b$12$50eN8MSIm9KDRpzmGL4JQO9gGy.2MDAafSOtqu9mZwfkb7jh33j26'
    )
    password_salt = (
        '$2b$12$50eN8MSIm9KDRpzmGL4JQO'
    )

    assert compare_plaintext_to_hash(
        'password', password_hash, password_salt) is True
    assert compare_plaintext_to_hash(
        'fakepassword', password_hash, password_salt) is False


def test_compare_plaintext_to_hash_no_password():
    with pytest.raises(AttributeError):
        compare_plaintext_to_hash(None, 'hash', 'salt')
