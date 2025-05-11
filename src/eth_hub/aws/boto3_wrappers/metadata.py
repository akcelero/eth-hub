from uuid import UUID

from botocore.exceptions import ClientError
from mypy_boto3_kms import KMSClient

from eth_hub.aws.boto3_wrappers.dto import (
    DescribeKeyResponse,
    KeyMetadata,
    ListAliasesPage,
)
from eth_hub.aws.boto3_wrappers.exceptions import (
    CantCreateKeyObjectAwsError,
    CantGetKeyInfoAwsError,
    CantListAliasesAwsError,
)


def set_alias(client: KMSClient, key_id: UUID, alias: str) -> None:
    try:
        client.create_alias(
            AliasName=f"alias/{alias}",
            TargetKeyId=str(key_id),
        )
    except ClientError as exception:
        raise CantCreateKeyObjectAwsError(exception)  # from exception


def get_aliases(client: KMSClient, key_id: UUID) -> list[str]:
    try:
        response = client.list_aliases(KeyId=str(key_id))
    except ClientError as error:
        raise CantListAliasesAwsError(error)

    page = ListAliasesPage.model_validate(response)
    return [alias.name.removeprefix("alias/") for alias in page.aliases]


def check_alias_already_taken(client: KMSClient, alias: str) -> bool:
    try:
        paginator = client.get_paginator("list_aliases")
        return any(
            alias_item.name == f"alias/{alias}"
            for page in paginator.paginate()
            for alias_item in ListAliasesPage.model_validate(page).aliases
        )
    except ClientError as error:
        raise CantListAliasesAwsError(error)


def get_key_metadata(client: KMSClient, key_id: UUID) -> KeyMetadata:
    try:
        response_raw = client.describe_key(KeyId=str(key_id))
    except ClientError as error:
        raise CantGetKeyInfoAwsError(error)

    response = DescribeKeyResponse.model_validate(response_raw)
    return response.key_metadata
