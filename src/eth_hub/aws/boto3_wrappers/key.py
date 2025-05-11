import datetime
from uuid import UUID

from botocore.exceptions import ClientError
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec, padding
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey
from mypy_boto3_kms import KMSClient
from mypy_boto3_kms.literals import (
    AlgorithmSpecType,
    DataKeyPairSpecType,
    WrappingKeySpecType,
)
from pydantic import SecretBytes

from eth_hub.aws.boto3_wrappers.dto import (
    CreateKeyItemResponse,
    GetPublicKeyResponse,
    ListKeysPage,
    ScheduleDeletionResponse,
)
from eth_hub.aws.boto3_wrappers.exceptions import (
    CantCreateKeyObjectAwsError,
    CantDeleteKeyAwsError,
    CantGetAddressAwsError,
    CantImportKeyMaterialAwsError,
    CantListKeysAwsError,
)
from eth_hub.aws.boto3_wrappers.utils import public_key_to_address

CUSTOMER_MASTER_KEY_SPEC: DataKeyPairSpecType = "ECC_SECG_P256K1"
WRAPPING_ALGORITHM: AlgorithmSpecType = "RSAES_OAEP_SHA_256"
WRAPPING_KEY_SPEC: WrappingKeySpecType = "RSA_2048"


def create_key_item(client: KMSClient, create_key_by_aws: bool) -> UUID:
    try:
        response_raw = client.create_key(
            KeyUsage="SIGN_VERIFY",
            CustomerMasterKeySpec=CUSTOMER_MASTER_KEY_SPEC,
            Origin="AWS_KMS" if create_key_by_aws else "EXTERNAL",
        )
    except ClientError as error:
        raise CantCreateKeyObjectAwsError(error)

    response = CreateKeyItemResponse.model_validate(response_raw)
    return response.key_metadata.key_id


def fulfil_private_key(
    client: KMSClient, key_id: UUID, private_key: SecretBytes
) -> None:
    import_params = client.get_parameters_for_import(
        KeyId=str(key_id),
        WrappingAlgorithm=WRAPPING_ALGORITHM,
        WrappingKeySpec=WRAPPING_KEY_SPEC,
    )

    wrapping_public_key = import_params["PublicKey"]
    import_token = import_params["ImportToken"]

    encrypted_key_material = _wrap_private_key(wrapping_public_key, private_key)

    try:
        client.import_key_material(
            KeyId=str(key_id),
            ImportToken=import_token,
            EncryptedKeyMaterial=encrypted_key_material,
            ExpirationModel="KEY_MATERIAL_DOES_NOT_EXPIRE",
        )
    except ClientError as error:
        raise CantImportKeyMaterialAwsError(error)


def get_key_ids(client: KMSClient) -> list[UUID]:
    try:
        paginator = client.get_paginator("list_keys")
        return [
            key.key_id
            for page in paginator.paginate()
            for key in ListKeysPage.model_validate(page).keys
        ]
    except ClientError as error:
        raise CantListKeysAwsError(error)


def get_address(client: KMSClient, key_id: UUID) -> bytes:
    try:
        response_raw = client.get_public_key(KeyId=str(key_id))
    except ClientError as error:
        raise CantGetAddressAwsError(error)

    response = GetPublicKeyResponse.model_validate(response_raw)
    return public_key_to_address(response.public_key)


def schedule_key_deletion(
    client: KMSClient, key_id: UUID, days_period=7
) -> datetime.datetime:
    try:
        response = client.schedule_key_deletion(
            KeyId=str(key_id), PendingWindowInDays=days_period
        )
    except ClientError as error:
        raise CantDeleteKeyAwsError(error)

    return ScheduleDeletionResponse.model_validate(response).deletion_datetime


def _wrap_private_key(wrapping_public_key: bytes, private_key: SecretBytes) -> bytes:
    backend = default_backend()
    int_private_key = int.from_bytes(private_key.get_secret_value(), byteorder="big")

    der_key = ec.derive_private_key(int_private_key, ec.SECP256K1(), backend)

    der_private_key = der_key.private_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )

    wrapping_public_key_der = serialization.load_der_public_key(
        wrapping_public_key, backend
    )

    if not isinstance(wrapping_public_key_der, RSAPublicKey):
        raise TypeError("Wrapping key must be an RSA public key.")

    return wrapping_public_key_der.encrypt(
        der_private_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )
