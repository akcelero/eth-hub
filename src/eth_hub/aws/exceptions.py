from eth_hub.aws.boto3_wrappers.exceptions import BaseAwsError


class BaseError(Exception):
    pass


class AliasAlreadyTakenError(BaseError):
    pass


class KeyNotFound(BaseError):
    pass


class CantFindValidVError(BaseError):
    pass


class BaseFromAwsError(BaseError):
    message = "Base error"

    def __init__(self, aws_error: BaseAwsError) -> None:
        self.code = aws_error.code
        super().__init__(f"{self.message}: {self.code}")


class CantGetKeyInfoError(BaseFromAwsError):
    message = "Can't get key info"


class CantListKeysError(BaseFromAwsError):
    message = "Can't list keys"


class CantCreateKeyError(BaseFromAwsError):
    message = "Can't create key"


class CantSetAlias(BaseFromAwsError):
    message = "Can't set alias"


class CantSignHash(BaseFromAwsError):
    message = "Can't sign hash"


class CantRemoveKey(BaseFromAwsError):
    message = "Can't remove key"
