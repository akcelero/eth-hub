from uuid import UUID

from asn1crypto.algos import DSASignature  # type: ignore
from botocore.exceptions import ClientError
from mypy_boto3_kms import KMSClient

from eth_hub.aws.boto3_wrappers.dto import SignResponse
from eth_hub.aws.boto3_wrappers.exceptions import CantSignMessage


def sign_message(client: KMSClient, key_id: UUID, message_hash: bytes) -> DSASignature:
    try:
        response = client.sign(
            KeyId=str(key_id),
            Message=message_hash,
            MessageType="DIGEST",
            SigningAlgorithm="ECDSA_SHA_256",
        )
    except ClientError as error:
        raise CantSignMessage(error)

    der_signature = SignResponse.model_validate(response).signature
    return DSASignature.load(der_signature)
