import hashlib


MAX_USERNAME_LEN = 25


def validate_username(username: str) -> bool:
    if len(username) > MAX_USERNAME_LEN:
        return False
    return True


def hash_salty(password: str) -> str:
    salt = hashlib.shake_128(password.encode('utf-8')).hexdigest(32)
    return hashlib.sha512((salt + password).encode('utf-8'), usedforsecurity=True).hexdigest()
