from typing import Optional
from uuid import UUID

import boto3
from eth_keys import keys
from mypy_boto3_kms import KMSClient
from pydantic import SecretBytes
from typing_extensions import override

from eth_hub.aws.boto3_wrappers.dto import KeyState
from eth_hub.aws.boto3_wrappers.exceptions import BaseAwsError
from eth_hub.aws.boto3_wrappers.key import (
    create_key_item,
    fulfil_private_key,
    get_address,
    get_key_ids,
    schedule_key_deletion,
)
from eth_hub.aws.boto3_wrappers.metadata import (
    check_alias_already_taken,
    get_aliases,
    get_key_metadata,
    set_alias,
)
from eth_hub.aws.boto3_wrappers.signature import sign_message
from eth_hub.aws.exceptions import (
    AliasAlreadyTakenError,
    CantCreateKeyError,
    CantFindValidVError,
    CantGetKeyInfoError,
    CantListKeysError,
    CantRemoveKey,
    CantSetAlias,
    CantSignHash,
    KeyNotFound,
)
from eth_hub.aws.key import AwsKey
from eth_hub.base_key_storage import BaseKeyStore
from eth_hub.signatureinfo import SignatureInfo

SECP256K1_ORDER = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141


class AwsKeyStore(BaseKeyStore):
    def __init__(self, boto3_client: Optional[KMSClient] = None):
        self.boto3_client = boto3_client or boto3.client("kms")

    @override
    def import_key(self, private_key: bytes) -> AwsKey:
        try:
            key_id = create_key_item(
                client=self.boto3_client,
                create_key_by_aws=False,
            )
            fulfil_private_key(
                client=self.boto3_client,
                key_id=key_id,
                private_key=SecretBytes(private_key),
            )
        except BaseAwsError as error:
            raise CantCreateKeyError(error)

        return self.get_key(key_id=key_id)

    @override
    def create_key(self) -> AwsKey:
        try:
            key_id = create_key_item(
                client=self.boto3_client,
                create_key_by_aws=True,
            )
        except BaseAwsError as error:
            raise CantCreateKeyError(error)

        return self.get_key(key_id=key_id)

    @override
    def get_key(self, key_id: UUID) -> AwsKey:
        try:
            if key := self._get_key(key_id, only_enabled=False):
                return key
        except BaseAwsError as error:
            raise CantGetKeyInfoError(error)

        raise KeyNotFound

    @override
    def list_keys(self, only_enabled: bool = True) -> list[AwsKey]:
        try:
            return [
                key
                for key_id in get_key_ids(client=self.boto3_client)
                if (key := self._get_key(key_id, only_enabled))
            ]

        except BaseAwsError as error:
            raise CantListKeysError(error)

    @override
    def remove_key(self, key_id: UUID) -> None:
        try:
            schedule_key_deletion(client=self.boto3_client, key_id=key_id)
        except BaseAwsError as error:
            raise CantRemoveKey(error)

    @override
    def sign_hash(self, key_id: UUID, hash_: bytes) -> SignatureInfo:
        try:
            dsa_signature = sign_message(
                client=self.boto3_client,
                key_id=key_id,
                message_hash=hash_,
            )
        except BaseAwsError as error:
            raise CantSignHash(error)

        r: int = dsa_signature["r"].native  # type: ignore
        s: int = dsa_signature["s"].native  # type: ignore

        if s > SECP256K1_ORDER // 2:
            s = SECP256K1_ORDER - s

        v = self._find_v(key_id, hash_, r, s)

        return SignatureInfo(key_id=key_id, hash=hash_, v=v, r=r, s=s)

    def set_alias(self, key_id: UUID, alias: str) -> None:
        try:
            if check_alias_already_taken(self.boto3_client, alias):
                raise AliasAlreadyTakenError

            set_alias(client=self.boto3_client, key_id=key_id, alias=alias)
        except BaseAwsError as error:
            raise CantSetAlias(error)

    def _find_v(self, key_id: UUID, message_hash: bytes, r: int, s: int) -> int:
        address = get_address(client=self.boto3_client, key_id=key_id)

        for v in (0, 1):
            signature = keys.Signature(vrs=(v, r, s))
            recovered_address = signature.recover_public_key_from_msg_hash(message_hash)

            if recovered_address.to_canonical_address() == address:
                return v

        raise CantFindValidVError

    def _get_key(self, key_id: UUID, only_enabled: bool) -> Optional[AwsKey]:
        metadata = get_key_metadata(client=self.boto3_client, key_id=key_id)

        if only_enabled and metadata.key_state != KeyState.ENABLED:
            return None

        aliases = get_aliases(client=self.boto3_client, key_id=key_id)
        address = get_address(client=self.boto3_client, key_id=key_id)
        return AwsKey(id=metadata.key_id, address=address, aliases=aliases or [])
