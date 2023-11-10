import hashlib


MAX_USERNAME_LEN = 25


def validate_username(username: str) -> bool:
    if len(username) > MAX_USERNAME_LEN or len(username) < 1:
        return False
    return True


def hash_salty(password: str) -> str:
    salt = hashlib.shake_128(password.encode('utf-8')).hexdigest(32)
    return hashlib.sha512((salt + password).encode('utf-8'), usedforsecurity=True).hexdigest()


# thanks to lakmatiol (207089259730042881), in pydis
def merge(a: dict, b: dict, /, merge_lists: bool = True) -> dict:
    match (a, b):
        case (dict(x), dict(y)):
            x = x.copy()

            for k in y:
                x[k] = merge(x[k], y[k], merge_lists=merge_lists) if k in x else y[k]

            return x
        case (list(x), list(y)):
            return (x + y) if merge_lists else y
        case (_, y):
            return y
