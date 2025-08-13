import secrets

import pytest


@pytest.fixture
def private_key() -> bytes:
    return bytes.fromhex(secrets.token_hex(32))
