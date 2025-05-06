import datetime
from enum import StrEnum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ResponseMetadata(BaseModel):
    http_status_code: int = Field(..., alias="HTTPStatusCode")


class Error(BaseModel):
    code: str = Field(..., alias="Code")
    message: str = Field(..., alias="Message")


class Response(BaseModel):
    response_metadata: ResponseMetadata = Field(..., alias="ResponseMetadata")
    error: Optional[Error] = Field(None, alias="Error")


class KeyState(StrEnum):
    CREATING = "Creating"
    ENABLED = "Enabled"
    DISABLED = "Disabled"
    PENDING_DELETION = "PendingDeletion"
    PENDING_IMPORT = "PendingImport"
    PENDING_REPLICA_DELETION = "PendingReplicaDeletion"
    UNAVAILABLE = "Unavailable"
    UPDATING = "Updating"


class KeySpec(StrEnum):
    RSA_2048 = "RSA_2048"
    RSA_3072 = "RSA_3072"
    RSA_4096 = "RSA_4096"
    ECC_NIST_P256 = "ECC_NIST_P256"
    ECC_NIST_P384 = "ECC_NIST_P384"
    ECC_NIST_P521 = "ECC_NIST_P521"
    ECC_SECG_P256K1 = "ECC_SECG_P256K1"
    SYMMETRIC_DEFAULT = "SYMMETRIC_DEFAULT"
    HMAC_224 = "HMAC_224"
    HMAC_256 = "HMAC_256"
    HMAC_384 = "HMAC_384"
    HMAC_512 = "HMAC_512"
    SM2 = "SM2"


class KeyMetadata(BaseModel):
    key_id: UUID = Field(..., alias="KeyId")
    enabled: bool = Field(..., alias="Enabled")
    key_state: KeyState = Field(..., alias="KeyState")
    description: str = Field(..., alias="Description")
    key_spec: KeySpec = Field(..., alias="CustomerMasterKeySpec")


class AliasItem(BaseModel):
    name: str = Field(..., alias="AliasName")
    target_key_id: UUID = Field(..., alias="TargetKeyId")


class KeyItem(BaseModel):
    key_id: UUID = Field(..., alias="KeyId")


class ListAliasesPage(Response):
    aliases: list[AliasItem] = Field(..., alias="Aliases")


class ListKeysPage(Response):
    keys: list[KeyItem] = Field(..., alias="Keys")


class CreateKeyItemResponse(Response):
    key_metadata: KeyMetadata = Field(..., alias="KeyMetadata")


class GetPublicKeyResponse(Response):
    public_key: bytes = Field(..., alias="PublicKey")


class DescribeKeyResponse(Response):
    key_metadata: KeyMetadata = Field(..., alias="KeyMetadata")


class ScheduleDeletionResponse(Response):
    key_arn: str = Field(..., alias="KeyId")
    deletion_datetime: datetime.datetime = Field(..., alias="DeletionDate")
    key_state: KeyState = Field(..., alias="KeyState")
    days_period: int = Field(..., alias="PendingWindowInDays")


class SignResponse(Response):
    key_arn: str = Field(..., alias="KeyId")
    signature: bytes = Field(..., alias="Signature")
    signing_algorithm: bytes = Field(..., alias="SigningAlgorithm")
