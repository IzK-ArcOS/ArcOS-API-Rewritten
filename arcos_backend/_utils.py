import hashlib
from profanity import profanity

MAX_USERNAME_LEN = 25


def validate_username(username: str) -> bool:
    if len(username) > MAX_USERNAME_LEN or len(username) < 1 or profanity.contains_profanity(username):
        return False
    return True


def hash_salty(password: str) -> str:
    salt = hashlib.shake_128(password.encode('utf-8')).hexdigest(32)
    return hashlib.sha512((salt + password).encode('utf-8'), usedforsecurity=True).hexdigest()
