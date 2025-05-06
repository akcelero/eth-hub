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


## Planned Features:
- Integration with HashiCorp Vault's
