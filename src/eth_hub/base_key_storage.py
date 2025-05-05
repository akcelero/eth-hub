from abc import ABC, abstractmethod
from typing import Sequence, Any
from uuid import UUID

from eth_account.messages import SignableMessage

from eth_hub.base_key import BaseKey
from eth_hub.signatureinfo import SignatureInfo


class BaseKeyStore(ABC):
    @abstractmethod
    def import_key(self, private_key: bytes) -> BaseKey:
        pass

    @abstractmethod
    def create_key(self) -> BaseKey:
        pass

    @abstractmethod
    def get_key(self, key_id: UUID) -> BaseKey:
        pass

    @abstractmethod
    def list_keys(self) -> Sequence[BaseKey]:
        pass

    @abstractmethod
    def remove_key(self, key_id: UUID) -> None:
        pass

    @abstractmethod
    def sign_hash(self, key_id: UUID, hash_: bytes) -> SignatureInfo:
        pass

    @abstractmethod
    def sign_message(
        self, key_id: UUID, signable_message: SignableMessage
    ) -> SignatureInfo:
        pass

    @abstractmethod
    def sign_transaction(
        self, key_id: UUID, transaction_data: dict[str, Any]
    ) -> SignatureInfo:
        pass
