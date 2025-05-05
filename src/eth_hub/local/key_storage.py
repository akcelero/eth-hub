from typing import Any
from typing_extensions import override
from uuid import uuid4, UUID

from eth_account import Account
from eth_account.datastructures import SignedMessage
from eth_account.messages import SignableMessage
from eth_account.signers.local import LocalAccount
from eth_typing import Hash32

from eth_hub.signatureinfo import SignatureInfo
from eth_hub.base_key_storage import BaseKeyStore
from eth_hub.local.key import LocalKey


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
        return LocalKey(id=key_id, address=account.address)

    @override
    def list_keys(self) -> list[LocalKey]:
        return [
            LocalKey(id=key_id, address=account.address)
            for key_id, account in self._accounts.items()
        ]

    @override
    def remove_key(self, uuid: UUID) -> None:
        self._accounts.pop(uuid)

    @override
    def sign_hash(self, key_id: UUID, hash_: bytes) -> SignatureInfo:
        account: LocalAccount = self._accounts[key_id]
        hash32: Hash32 = Hash32(hash_)
        signed_message = account.unsafe_sign_hash(hash32)
        return self._get_signature_info(key_id, signed_message)

    @override
    def sign_message(
        self, key_id: UUID, signable_message: SignableMessage
    ) -> SignatureInfo:
        account: LocalAccount = self._accounts[key_id]
        signed_message = account.sign_message(signable_message)
        return self._get_signature_info(key_id, signed_message)

    @override
    def sign_transaction(
        self, key_id: UUID, transaction_data: dict[str, Any]
    ) -> SignatureInfo:
        account: LocalAccount = self._accounts[key_id]
        signature = account.sign_transaction(transaction_data)
        return SignatureInfo(
            key_id=key_id,
            hash=signature.hash,
            v=signature.v,
            r=f"0x{signature.r:064x}",
            s=f"0x{signature.s:064x}",
        )

    def _add_account(self, account: LocalAccount) -> LocalKey:
        key_id: UUID = uuid4()
        self._accounts[key_id] = account

        return LocalKey(id=key_id, address=account.address)

    def _get_signature_info(
        self, key_id: UUID, signed_message: SignedMessage
    ) -> SignatureInfo:
        return SignatureInfo(
            key_id=key_id,
            hash=signed_message.message_hash,
            v=signed_message.v,
            r=f"0x{signed_message.r:064x}",
            s=f"0x{signed_message.s:064x}",
        )
