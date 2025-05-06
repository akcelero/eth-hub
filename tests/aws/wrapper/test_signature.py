import uuid

from botocore.stub import Stubber
from mypy_boto3_kms import KMSClient
from eth_hash.auto import keccak

from eth_hub.aws.boto3_wrappers.signature import sign_message

def test_set_alias(client: KMSClient, stubber: Stubber) -> None:
    # given
    key_id = uuid.uuid4()
    signature = bytes.fromhex(
        "3046022100eb6c5e5503afdb89e0580c3aa25069323d8a050a707be5b08d115c084bd9cb"
        "1a022100a64ba0a49b3ac89eb67ef01fc1c1348bb46ae0b9caa06964b723ac426535f818"
    )
    msg_hash = keccak(b"test value")

    stubber.add_response(
        method="sign",
        service_response={
            "KeyId": f"arn:aws:kms:eu-west-2:111111111111:key/{key_id}",
            "Signature": signature,
            "SigningAlgorithm": "ECDSA_SHA_256",
            "ResponseMetadata": {
                "HTTPStatusCode": 200
            }
        }
    )

    # when
    signature_received = sign_message(client, key_id, msg_hash)

    # then
    stubber.assert_no_pending_responses()
    assert signature_received["r"].native == 0xeb6c5e5503afdb89e0580c3aa25069323d8a050a707be5b08d115c084bd9cb1a
    assert signature_received["s"].native == 0xa64ba0a49b3ac89eb67ef01fc1c1348bb46ae0b9caa06964b723ac426535f818
