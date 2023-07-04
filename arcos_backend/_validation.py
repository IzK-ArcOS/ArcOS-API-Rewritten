import string


ALLOWED_SYMBOLS = string.ascii_letters + string.digits + '_' + ' '


def validate_username(username: str) -> bool:
    for char in username:
        if char not in ALLOWED_SYMBOLS:
            return False
    return True
