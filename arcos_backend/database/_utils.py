import hashlib


def _enc(s: str) -> bytes:
    return s.encode('utf-8')


def hash_salty(password: str) -> str:
    return hashlib.sha512(_enc(hashlib.shake_128(_enc(password)).hexdigest(32) + password), usedforsecurity=True).hexdigest()
