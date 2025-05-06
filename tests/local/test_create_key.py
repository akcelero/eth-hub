from eth_hub.local.key_storage import LocalKeyStorage


def test_create_key() -> None:
    # given
    local_signer = LocalKeyStorage()

    # when
    key_info = local_signer.create_key()

    # then
    assert key_info.id in local_signer._accounts
