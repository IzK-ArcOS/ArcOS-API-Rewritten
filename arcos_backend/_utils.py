import hashlib
import json
import string


ALLOWED_SYMBOLS = string.ascii_letters + string.digits + '_' + ' '


def validate_username(username: str) -> bool:
    for char in username:
        if char not in ALLOWED_SYMBOLS:
            return False
    return True


def hash_salty(password: str) -> str:
    salt = hashlib.shake_128(password.encode('utf-8')).hexdigest(32)
    return hashlib.sha512((salt + password).encode('utf-8'), usedforsecurity=True).hexdigest()


def dict2json(o: dict) -> str:
    return json.JSONEncoder().encode(o)


def json2dict(s: str) -> dict:
    return json.JSONDecoder().decode(s)
