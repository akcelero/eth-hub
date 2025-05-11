# eth-hub - Ethereum Key Management Toolkit

[![CI/CD](https://github.com/akcelero/eth-hub/actions/workflows/run-tests.yaml/badge.svg?query=branch%3Amaster)](https://github.com/akcelero/eth-hub/actions)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)

[![PyPI Version](https://img.shields.io/pypi/v/eth-hub.svg)](https://pypi.org/project/eth-hub/)
![PyPI - Status](https://img.shields.io/pypi/status/eth-hub)

[![Python Versions](https://img.shields.io/pypi/pyversions/eth-hub.svg)](https://pypi.org/project/eth-hub/)
[![License](https://img.shields.io/pypi/l/eth-hub.svg)](https://github.com/akcelero/eth-hub/blob/main/LICENSE)

A secure abstraction layer for managing Ethereum keys across different storage backends.

## Key Features

🔐 **Secure Key Management**
- Unified interface for multiple key storage providers
- Never exposes private keys outside secure environments
- Will support both software and hardware security modules

📜 **Complete Signing Capabilities**
- Transaction signing
- Message signing (EIP-191 compatible)
- Hash signing
- Consistent signature output format

## Core Architecture

```python
from eth_hub import (
    BaseKeyStore,  # Abstract base class
    AwsKeyStore,  # AWS KMS implementation
    LocalKeyStore  # In-memory implementation
)
```

### BaseKeyStore (ABC)

The abstract base class defining all key operations:
```python
class BaseKeyStore(ABC):
    @abstractmethod
    def import_key(self, private_key: bytes) -> BaseKey: ...

    @abstractmethod
    def create_key(self) -> BaseKey: ...

    @abstractmethod
    def get_key(self, key_id: UUID) -> BaseKey: ...

    @abstractmethod
    def list_keys(self) -> Sequence[BaseKey]: ...

    @abstractmethod
    def remove_key(self, key_id: UUID) -> None: ...

    @abstractmethod
    def sign_hash(self, key_id: UUID, hash_: bytes) -> SignatureInfo: ...

    @abstractmethod
    def sign_message(self, key_id: UUID, message: SignableMessage) -> SignatureInfo: ...

    @abstractmethod
    def sign_transaction(self, key_id: UUID, transaction_data: dict[str, Any]) -> SignatureInfo: ...
```

### Current Implementations

#### 1. AWS KMS KeyStore

- Keys never leave AWS KMS
- All signing operations performed within KMS
- Supports both imported and KMS-generated keys

#### 2. LocalKeyStore (Memory)

- In-memory key storage for development/testing
- Simulates same interface as other stores
- Useful for CI/CD pipelines and local testing

#### 3. HashiCorp Vaul - WiP

## Installation
```bash
pip install eth-hub
```

## Aws usage case
If you want to use your own key material, you can import it into AWS KMS. Otherwise, create a new KMS key for Ethereum signing.
```Python
web3_rpc = "..."
web3 = Web3(Web3.HTTPProvider(web3_rpc))

key_storage = AwsKeyStore(boto3.client("kms"))

# import your private key to KMS
key = key_storage.import_key(private_key="...")

# or create new one by KMS:
key = key_storage.create_key()
```

Sign and send transaction:
```Python
web3_rpc = "..."
web3 = Web3(Web3.HTTPProvider(web3_rpc))

key_id = "..."
key_storage = AwsKeyStore(boto3.client("kms"))
key = key_storage.get_key(key_id)
user_address = Web3.to_checksum_address(key.address.hex())

abi = [...]
contract_address = Web3.to_checksum_address(contract_address)
contract = web3.eth.contract(address=contract_address, abi=abi)
nonce = web3.eth.get_transaction_count(user_address)
transaction_dict = contract.functions.foo.build_transaction({"nonce": nonce})

unsigned_transaction = TypedTransaction.from_dict(transaction_dict)
signature = key_storage.sign_hash(key_id, unsigned_transaction.hash())

signed_transaction = TypedTransaction.from_dict(
    {**transaction_dict, "v": signature.v, "r": signature.r, "s": signature.s}
)

tx_hash = web3.eth.send_raw_transaction(encoded_tx.encode())
```
The private key never leaves AWS KMS. Signing is performed inside KMS, and only the signature is returned to your application.


## Planned Features:
- Integration with HashiCorp Vault's
