import base64


def parse_basic(value: str) -> tuple[str, str]:
    if not value.startswith('Basic '):
        raise ValueError("invalid format")

    username, password = base64.b64decode(value[6:]).decode('utf-8').split(':')
    return username, password
