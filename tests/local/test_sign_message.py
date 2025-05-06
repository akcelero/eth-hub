import uuid
from unittest.mock import Mock

from eth_account.messages import encode_defunct

from eth_hub.signatureinfo import SignatureInfo
from eth_hub.local.key_storage import LocalKeyStorage


def test_create_key(account_mock: Mock, signed_message_mock: Mock) -> None:
    # given
    key_id = uuid.uuid4()
    local_signer = LocalKeyStorage()
    local_signer._accounts[key_id] = account_mock
    message = encode_defunct(text="test message")

    # when
    signature = local_signer.sign_message(key_id=key_id, signable_message=message)

    # then
    assert isinstance(signature, SignatureInfo)
    assert signature.key_id == key_id
    assert signature.hash == signed_message_mock.message_hash.encode()
    assert signature.v == signed_message_mock.v
    assert signature.r == f"0x{signed_message_mock.r:064x}"
    assert signature.s == f"0x{signed_message_mock.s:064x}"
    account_mock.sign_message.assert_called_once()
