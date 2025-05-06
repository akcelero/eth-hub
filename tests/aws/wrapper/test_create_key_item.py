import uuid
import datetime

import pytest

from botocore.stub import Stubber
from mypy_boto3_kms import KMSClient
from pydantic import SecretBytes

from eth_hub.aws.boto3_wrappers.dto import KeyState, KeySpec
from eth_hub.aws.boto3_wrappers.key import (
    create_key_item,
    fulfil_private_key,
    get_key_ids,
    get_address,
    schedule_key_deletion
)
from eth_hub.aws.boto3_wrappers.exceptions import BaseAwsError


WRAPPING_KEY = bytes.fromhex("""
30820122300d06092a864886f70d01010105000382010f003082010a0282010100e4823c943c43a114fb77
b7776b62a8fbf80c51e4df2776c49e804f847b56d01ac688223af6d1d58172b4ddf6d24c0d6af06c4befe8
1439d3e3f3308d5bcfa5c7f9f080b53c3409a8056253b2dad7ccdee5ef7b6bf199f1e4b8df341e9155382f
52045236aee0225e153cd492ca99cda93905b9070a47e20d6680272e854b7b9911958f3b2dbe2495564a7b
9831071b2a60351103614fbaf21b51e09add4a3952a87c23188182837665bce1f54a6dc86c05116e249b71
60b03a48adc8335f64ee59d81f3b2f33b7f149b43d88f7409d572e03d9e717fce57795847077203e813cef
703edcc29d2af3d8d4f2a4dedc2bcc2d2d0cf9ad31d7542cf69dc7b6c279b90203010001
""")


def test_create_key_item(client: KMSClient, stubber: Stubber) -> None:
    # given
    key_id = uuid.uuid4()

    stubber.add_response(
        method="create_key",
        service_response={
            "KeyMetadata": {
                "KeyId": str(key_id),
                "Enabled": True,
                "KeyState": KeyState.ENABLED.value,
                "Description": "Test Key",
                "CustomerMasterKeySpec": KeySpec.ECC_SECG_P256K1.value,
                "CreationDate": datetime.datetime.now(datetime.UTC),
            },
            "ResponseMetadata": {
                "HTTPStatusCode": 200
            }
        }
    )

    # when
    retrieved_key_id = create_key_item(client, create_key_by_aws=True)

    # then
    assert retrieved_key_id == key_id
    stubber.assert_no_pending_responses()


def test_create_key_item_error(client: KMSClient, stubber: Stubber) -> None:
    # given
    stubber.add_client_error(
        method="create_key",
        service_error_code="AccessDeniedException",
        service_message="You do not have sufficient permissions to perform this action.",
        http_status_code=403
    )

    # when / then
    with pytest.raises(BaseAwsError):
        create_key_item(client, create_key_by_aws=True)

    stubber.assert_no_pending_responses()

def test_fulfil_private_key(client: KMSClient, stubber: Stubber) -> None:
    # given
    key_id = uuid.uuid4()

    stubber.add_response(
        method="get_parameters_for_import",
        service_response={
            "KeyId": f"arn:aws:kms:eu-west-2:222222222222:key/{key_id}",
            "ImportToken": b"test",
            "PublicKey": WRAPPING_KEY,
            "ParametersValidTo": "2025-02-04T14:30:00.000000",
            "ResponseMetadata": {
                "HTTPStatusCode": 200
            }
        }
    )
    stubber.add_response(
        method="import_key_material",
        service_response={
        "ResponseMetadata": {
                "HTTPStatusCode": 200
            }
        }
    )

    # when
    fulfil_private_key(client=client, key_id=key_id, private_key=SecretBytes(b"1"))

    # then
    stubber.assert_no_pending_responses()


def test_get_key_ids(client: KMSClient, stubber: Stubber) -> None:
    # given
    key_id_1 = uuid.uuid4()
    key_id_2 = uuid.uuid4()

    stubber.add_response(
        method="list_keys",
        service_response={
            "Keys": [
                {
                    "KeyId": str(key_id_1),
                    "KeyArn": f"arn:aws:kms:eu-west-2:111111111111:key/{key_id_1}"
                }
            ],
            "NextMarker": "next-marker-1",  # Correct pagination key for KMS
            "Truncated": True,
            "ResponseMetadata": {
                "HTTPStatusCode": 200
            }
        }
    )
    stubber.add_response(
        method="list_keys",
        service_response={
            "Keys": [
                {
                    "KeyId": str(key_id_2),
                    "KeyArn": f"arn:aws:kms:eu-west-2:111111111111:key/{key_id_2}"
                }
            ],
            "Truncated": False,
            "ResponseMetadata": {
                "HTTPStatusCode": 200
            }
        }
    )

    # when
    key_ids = get_key_ids(client)

    # then
    stubber.assert_no_pending_responses()
    assert key_ids == [key_id_1, key_id_2]


def test_get_address(client: KMSClient, stubber: Stubber) -> None:
    # given
    key_id = uuid.uuid4()
    public_key = bytes.fromhex(
        "3056301006072a8648ce3d020106052b8104000a034200042d3665dce3d34dfdbcc585ffdee7f7b245f01685"
        "d228a3d1c04ea80805282c54bf66263c4c0d2a8c0bdb0ba0f888d1f9b4a8b14325d8b39492b684afcb16e1e6"
    )
    address = "9c60ee98a12d30ca9eaccc9635a10864756a00d7"

    stubber.add_response(
        method="get_public_key",
        service_response={
            "PublicKey": public_key,
            "ResponseMetadata": {
                "HTTPStatusCode": 200
            }
        }
    )

    # when
    address_received = get_address(client, key_id=key_id)

    # then
    stubber.assert_no_pending_responses()
    assert address_received.hex() == address


def test_schedule_key_deletion(client: KMSClient, stubber: Stubber) -> None:
    # given
    key_id = uuid.uuid4()
    deletion_date = datetime.datetime.now(datetime.UTC)

    stubber.add_response(
        method="schedule_key_deletion",
        service_response={
            "DeletionDate": deletion_date,
            "KeyId": f"arn:aws:kms:eu-west-2:237149049208:key/{key_id}",
            "KeyState": "PendingDeletion",
            "PendingWindowInDays": 7,
            "ResponseMetadata": {
                "HTTPStatusCode": 200,
            }
        }
    )

    # when
    deletion_date_received = schedule_key_deletion(client, key_id=key_id)

    # then
    stubber.assert_no_pending_responses()
    assert deletion_date == deletion_date_received
