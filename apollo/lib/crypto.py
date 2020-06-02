import binascii

from Crypto import Random


def get_random_hex_token(number_of_bytes):
    if number_of_bytes == 0:
        return ""
    elif number_of_bytes < 0:
        raise ValueError("Number of bytes can't be negative")
    elif number_of_bytes % 2 != 0:
        raise ValueError("Number of bytes needs to be even")

    # We convert the bytes to hexadecimal which will double the length of the
    # string.
    return binascii.b2a_hex(
        Random.get_random_bytes(int(number_of_bytes / 2))
    ).decode('utf-8')
