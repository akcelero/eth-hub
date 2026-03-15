import uuid

from botocore.stub import Stubber
from eth_hash.auto import keccak
from mypy_boto3_kms import KMSClient

from eth_hub.aws.boto3_wrappers.signature import sign_message


def test_set_alias(client: KMSClient, stubber: Stubber) -> None:
    # given
    key_id = uuid.uuid4()
    signature = bytes.fromhex(
        "3046022100eb6c5e5503afdb89e0580c3aa25069323d8a050a707be5b08d115c084bd9cb"
        "1a022100a64ba0a49b3ac89eb67ef01fc1c1348bb46ae0b9caa06964b723ac426535f818",
    )
    msg_hash = keccak(b"test value")
    expected_r = 0xEB6C5E5503AFDB89E0580C3AA25069323D8A050A707BE5B08D115C084BD9CB1A
    expected_s = 0xA64BA0A49B3AC89EB67EF01FC1C1348BB46AE0B9CAA06964B723AC426535F818

    stubber.add_response(
        method="sign",
        service_response={
            "KeyId": f"arn:aws:kms:eu-west-2:111111111111:key/{key_id}",
            "Signature": signature,
            "SigningAlgorithm": "ECDSA_SHA_256",
            "ResponseMetadata": {
                "HTTPStatusCode": 200,
            },
        },
    )

    # when
    signature_received = sign_message(client, key_id, msg_hash)

    # then
    stubber.assert_no_pending_responses()
    assert signature_received["r"].native == expected_r
    assert signature_received["s"].native == expected_s
