from uuid import UUID, uuid4

from eth_account import Account
from eth_account.signers.local import LocalAccount
from eth_typing import Hash32
from typing_extensions import override

from eth_hub.base_key_storage import BaseKeyStore
from eth_hub.local.key import LocalKey
from eth_hub.signatureinfo import SignatureInfo


class LocalKeyStorage(BaseKeyStore):
    def __init__(self) -> None:
        self._accounts: dict[UUID, LocalAccount] = {}

    @override
    def import_key(self, private_key: bytes) -> LocalKey:
        account: LocalAccount = Account.from_key(private_key)
        return self._add_account(account)

    @override
    def create_key(self) -> LocalKey:
        account: LocalAccount = Account.create()
        return self._add_account(account)

    @override
    def get_key(self, key_id: UUID) -> LocalKey:
        account: LocalAccount = self._accounts[key_id]
        address = self._get_bytes_address(account.address)
        return LocalKey(id=key_id, address=address)

    @override
    def list_keys(self) -> list[LocalKey]:
        return [
            LocalKey(id=key_id, address=self._get_bytes_address(account.address))
            for key_id, account in self._accounts.items()
        ]

    @override
    def remove_key(self, key_id: UUID) -> None:
        self._accounts.pop(key_id)

    @override
    def sign_hash(self, key_id: UUID, hash_: bytes) -> SignatureInfo:
        account: LocalAccount = self._accounts[key_id]
        hash32: Hash32 = Hash32(hash_)
        signed_message = account.unsafe_sign_hash(hash32)
        return SignatureInfo(
            key_id=key_id,
            hash=signed_message.message_hash,
            v=signed_message.v,
            r=signed_message.r,
            s=signed_message.s,
        )

    def _add_account(self, account: LocalAccount) -> LocalKey:
        key_id: UUID = uuid4()
        self._accounts[key_id] = account
        address = bytes.fromhex(account.address.removeprefix("0x"))

        return LocalKey(id=key_id, address=address)

    def _get_bytes_address(self, address: str) -> bytes:
        return bytes.fromhex(address.removeprefix("0x"))
