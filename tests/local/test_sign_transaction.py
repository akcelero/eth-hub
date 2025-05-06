import uuid
from unittest.mock import Mock


from eth_hub.signatureinfo import SignatureInfo
from eth_hub.local.key_storage import LocalKeyStorage


def test_create_key(account_mock: Mock, signed_tx_mock: Mock) -> None:
    # given
    key_id = uuid.uuid4()
    local_signer = LocalKeyStorage()
    local_signer._accounts[key_id] = account_mock

    # when
    transaction_data = {
        "nonce": 123,
        "gas_price": 123,
        "gas_limit": 123,
        "to": "0x09616C3d61b3331fc4109a9E41a8BDB7d9776609",
        "chain_id": 1,
        "value": 123
    }
    signature = local_signer.sign_transaction(
        key_id=key_id,
        transaction_data=transaction_data
    )

    # then
    assert isinstance(signature, SignatureInfo)
    assert signature.key_id == key_id
    assert signature.hash == signed_tx_mock.hash.encode()
    assert signature.v == signed_tx_mock.v
    assert signature.r == f"0x{signed_tx_mock.r:064x}"
    assert signature.s == f"0x{signed_tx_mock.s:064x}"
    account_mock.sign_transaction.assert_called_once()
