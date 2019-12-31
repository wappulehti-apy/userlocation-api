from base64 import b64encode
from config import Testing as config


def with_auth(original={}):
    """Helper function for adding authentication headers."""
    username = config.BASIC_AUTH_USERNAME
    password = config.BASIC_AUTH_PASSWORD

    token = b64encode(bytes(f'{username}:{password}', 'ascii')).decode('ascii')
    auth = {'Authorization': f'Basic {token}'}

    return {**original, **auth}
