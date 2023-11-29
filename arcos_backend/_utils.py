import hashlib
from better_profanity import profanity as better_profanity
from profanity import profanity

MAX_USERNAME_LEN = 25


def validate_username(username: str) -> bool:
    if len(username) > MAX_USERNAME_LEN or len(username) < 1:
        return False
    return True


def check_profanity(username: str) -> bool:
    return profanity.contains_profanity(username) or better_profanity.contains_profanity(username)


def hash_salty(password: str) -> str:
    salt = hashlib.shake_128(password.encode('utf-8')).hexdigest(32)
    return hashlib.sha512((salt + password).encode('utf-8'), usedforsecurity=True).hexdigest()
