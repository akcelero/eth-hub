import datetime
from typing import Optional
from uuid import UUID, uuid4

from eth_account import Account
from eth_account.signers.local import LocalAccount
from mypy_boto3_kms.client import KMSClient
from pydantic import BaseModel, SecretBytes, ConfigDict
from pytest_mock import MockerFixture

from eth_hub.aws.boto3_wrappers.dto import KeyState, KeyMetadata, KeySpec
from eth_hub.aws.boto3_wrappers.exceptions import CantGetAddressAwsError, CantCreateKeyObjectAwsError


class Key(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    id: UUID
    aliases: list[str] = []
    account: Optional[LocalAccount] = None
    key_state: KeyState = KeyState.ENABLED
    removal_scheduled: bool = False
    enabled: bool = True


class AwsMock:
    def __init__(self, mocker: MockerFixture) -> None:
        self.keys: dict[UUID, Key] = {}

        self.create_key_item_mock = mocker.patch(
            "eth_hub.aws.key_store.create_key_item",
            side_effect=self.create_key_item
        )

        self.fulfil_private_key_mock = mocker.patch(
            "eth_hub.aws.key_store.fulfil_private_key",
            side_effect=self.fulfil_private_key
        )

        self.get_key_ids_mock = mocker.patch(
            "eth_hub.aws.key_store.get_key_ids",
            side_effect=self.get_key_ids
        )

        self.get_address_mock = mocker.patch(
            "eth_hub.aws.key_store.get_address",
            side_effect=self.get_address
        )

        self.schedule_key_deletion_mock = mocker.patch(
            "eth_hub.aws.key_store.schedule_key_deletion",
            side_effect=self.schedule_key_deletion
        )

        self.set_alias_mock = mocker.patch(
            "eth_hub.aws.key_store.set_alias",
            side_effect=self.set_alias
        )

        self.get_aliases_mock = mocker.patch(
            "eth_hub.aws.key_store.get_aliases",
            side_effect=self.get_aliases
        )

        self.check_alias_already_taken_mock = mocker.patch(
            "eth_hub.aws.key_store.check_alias_already_taken",
            side_effect=self.check_alias_already_taken
        )

        self.get_key_metadata_mock = mocker.patch(
            "eth_hub.aws.key_store.get_key_metadata",
            side_effect=self.get_key_metadata
        )

    def create_key_item(self, client: KMSClient, create_key_by_aws: bool) -> UUID:
        key_id = uuid4()
        self.keys[key_id] = Key(id=key_id)
        if create_key_by_aws:
            self.keys[key_id].account = Account.create()

        return key_id

    def fulfil_private_key(self, client: KMSClient, key_id: UUID, private_key: SecretBytes) -> None:
        self.keys[key_id].account = Account.from_key(private_key.get_secret_value())

    def get_key_ids(self, client: KMSClient) -> list[UUID]:
        return list(self.keys.keys())

    def get_address(self, client: KMSClient, key_id: UUID) -> bytes:
        if (key := self.keys[key_id]) and key.account is not None:
            return bytes.fromhex(key.account.address.removeprefix("0x"))

        raise CantGetAddressAwsError()

    def schedule_key_deletion(self, client: KMSClient, key_id: UUID, days_period=7) -> datetime.datetime:
        self.keys[key_id].removal_scheduled = True
        return datetime.datetime.now(datetime.UTC) + datetime.timedelta(days=days_period)

    def set_alias(self, client: KMSClient, key_id: UUID, alias: str) -> None:
        if self.check_alias_already_taken(client, alias):
            raise CantCreateKeyObjectAwsError()

        self.keys[key_id].aliases.append(alias)

    def get_aliases(self, client: KMSClient, key_id: UUID) -> list[str]:
        return self.keys[key_id].aliases

    def check_alias_already_taken(self, client: KMSClient, alias: str) -> bool:
        return any(alias in key.aliases for key in list(self.keys.values()))

    def get_key_metadata(self, client: KMSClient, key_id: UUID) -> KeyMetadata:
        return KeyMetadata(
            KeyId=key_id,
            Enabled=self.keys[key_id].enabled,
            KeyState=self.keys[key_id].key_state,
            Description="",
            CustomerMasterKeySpec=KeySpec.ECC_SECG_P256K1
        )
