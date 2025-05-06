import datetime
import uuid

from botocore.stub import Stubber
from mypy_boto3_kms import KMSClient

from eth_hub.aws.boto3_wrappers.dto import KeyState, KeySpec
from eth_hub.aws.boto3_wrappers.metadata import set_alias, check_alias_already_taken, \
    get_key_metadata, get_aliases


def test_set_alias(client: KMSClient, stubber: Stubber) -> None:
    # given
    key_id = uuid.uuid4()

    stubber.add_response(
        method="create_alias",
        service_response={
            "ResponseMetadata": {
                "HTTPStatusCode": 200
            }
        }
    )

    # when
    set_alias(client, key_id, "test")

    # then
    stubber.assert_no_pending_responses()


def test_get_aliases(client: KMSClient, stubber: Stubber) -> None:
    # given
    key_id = uuid.uuid4()
    alias1 = "test1"
    alias2 = "test2"

    stubber.add_response(
        method="list_aliases",
        service_response={
            "Aliases": [
                {
                    "AliasName": f"alias/{alias1}",
                    "TargetKeyId": str(key_id),
                }, {
                    "AliasName": f"alias/{alias2}",
                    "TargetKeyId": str(key_id),
                }
            ],
            "ResponseMetadata": {
                "HTTPStatusCode": 200
            }
        }
    )

    # when
    aliases = get_aliases(client, key_id)

    # then
    stubber.assert_no_pending_responses()
    assert aliases == [alias1, alias2]


def test_check_alias_already_taken(client: KMSClient, stubber: Stubber) -> None:
    # given
    key_id = uuid.uuid4()
    alias1 = "test1"
    alias2 = "test2"

    stubber.add_response(
        method="list_aliases",
        service_response={
            "Aliases": [
                {
                    "AliasName": f"alias/{alias1}",
                    "TargetKeyId": str(key_id),
                }, {
                    "AliasName": f"alias/{alias2}",
                    "TargetKeyId": str(key_id),
                }
            ],
            "ResponseMetadata": {
                "HTTPStatusCode": 200
            }
        }
    )

    # when
    alread_taken = check_alias_already_taken(client, alias1)

    # then
    stubber.assert_no_pending_responses()
    assert alread_taken is True


def test_get_key_metadata(client: KMSClient, stubber: Stubber) -> None:
    # given
    key_id = uuid.uuid4()
    enabled = True
    state = KeyState.ENABLED
    description = "Test Key"
    creation_date = datetime.datetime.now(datetime.UTC)

    stubber.add_response(
        method="describe_key",
        service_response={
            "KeyMetadata": {
                "KeyId": str(key_id),
                "Enabled": enabled,
                "KeyState": state.value,
                "Description": description,
                "CustomerMasterKeySpec": KeySpec.ECC_SECG_P256K1.value,
                "CreationDate": creation_date,
            },
            "ResponseMetadata": {
                "HTTPStatusCode": 200
            }
        }
    )

    # when
    key = get_key_metadata(client, key_id)

    # then
    stubber.assert_no_pending_responses()
    assert key_id == key.key_id
    assert key.enabled == enabled
    assert key.description == description
