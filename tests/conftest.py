import pytest
import secrets


@pytest.fixture(scope="function")
def private_key() -> bytes:
    return bytes.fromhex(secrets.token_hex(32))
