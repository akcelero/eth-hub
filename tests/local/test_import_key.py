from eth_account import Account

from eth_hub.local.key_storage import LocalKeyStorage


def test_create_key(private_key: str) -> None:
    # given
    local_signer = LocalKeyStorage()
    account = Account.create()

    # when
    key_info = local_signer.import_key(private_key=account._private_key)

    # then
    assert key_info.id in local_signer._accounts
    assert key_info.address == bytes.fromhex(account.address.removeprefix("0x"))
