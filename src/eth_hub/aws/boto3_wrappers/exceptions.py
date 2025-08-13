from botocore.exceptions import ClientError


class BaseAwsError(Exception):
    message = "Base error"

    def __init__(self, client_error: ClientError | None = None) -> None:
        if client_error is None:
            self.code = ""

        else:
            response = client_error.response
            self.code = response.get("Error", {}).get("Code", "")

        super().__init__(f"{self.message}: {self.code}")


class CantCreateKeyObjectAwsError(BaseAwsError):
    message = "Can't create key"


class CantImportKeyMaterialAwsError(BaseAwsError):
    message = "Can't import key"


class CantGetAddressAwsError(BaseAwsError):
    message = "Can't get address"


class CantDeleteKeyAwsError(BaseAwsError):
    message = "Can't delete key"


class CantListKeysAwsError(BaseAwsError):
    message = "Can't list keys"


class CantListAliasesAwsError(BaseAwsError):
    message = "Can't list aliases"


class CantGetKeyInfoAwsError(BaseAwsError):
    message = "Can't get key info"


class CantSignMessageError(BaseAwsError):
    message = "Can't sign message"


class NotRSAKeyError(BaseAwsError):
    message = "Must be an RSA public key."
