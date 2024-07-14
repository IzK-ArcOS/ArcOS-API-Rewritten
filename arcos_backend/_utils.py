from collections.abc import Iterable
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


def is_in(obj: object, it: Iterable[object]) -> bool:
    return any(obj is item for item in it)


def merge_into(target: dict, patch: dict, /, merge_lists: bool = True) -> None:
    for key, patch_v in [(p_k, p_v) for p_k, p_v in patch.items()]:
        if key in target and type(target[key]) is (patch_vt := type(patch_v)):
            if isinstance(patch_v, dict):
                merge_into(target[key], patch_v)
            elif merge_lists and is_in(patch_vt, (list, tuple)):
                target[key] += patch_v
            else:
                target[key] = patch_v
        elif patch_vt is dict:
            merge_into(target.setdefault(key, {}), patch_v)
        elif patch_v is None:
            if key in target:
                del target[key]
        else:
            target[key] = patch_v
