import pytest

from apollo.lib.crypto import get_random_hex_token


def test_random_hex_token():
    empty_result = get_random_hex_token(0)
    result_1 = get_random_hex_token(32)
    result_2 = get_random_hex_token(32)

    assert len(empty_result) == 0
    assert len(result_1.encode('utf-8')) == 32
    assert result_1 != result_2


def test_random_hex_token_negative_size():
    with pytest.raises(ValueError, match="Number of bytes can't be negative"):
        get_random_hex_token(-1)


def test_random_hex_token_uneven_bytes_number():
    with pytest.raises(ValueError, match="Number of bytes needs to be even"):
        get_random_hex_token(3)
