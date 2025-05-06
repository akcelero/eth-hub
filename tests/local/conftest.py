import pytest
from unittest.mock import Mock


@pytest.fixture(scope="function")
def signed_message_mock() -> Mock:
    mock = Mock()
    mock.message_hash = "mocked_hash"
    mock.v = 27
    mock.r = 0x0000000000000000000000000000000000000000000000000000000000000000
    mock.s = 0x0000000000000000000000000000000000000000000000000000000000000001

    return mock


@pytest.fixture(scope="function")
def signed_tx_mock() -> Mock:
    mock = Mock()
    mock.hash = "mocked_hash"
    mock.v = 28
    mock.r = 0x0000000000000000000000000000000000000000000000000000000000000002
    mock.s = 0x0000000000000000000000000000000000000000000000000000000000000003

    return mock


@pytest.fixture(scope="function")
def account_mock(signed_message_mock: Mock, signed_tx_mock: Mock) -> Mock:
    mock = Mock()
    mock.sign_message.return_value = signed_message_mock
    mock.sign_transaction.return_value = signed_tx_mock

    return mock
