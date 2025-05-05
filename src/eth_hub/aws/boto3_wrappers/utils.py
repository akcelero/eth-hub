from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import load_der_public_key
from eth_keys.datatypes import PublicKey


def public_key_to_address(public_key: bytes, safe: bool = True) -> bytes:
    if safe:
        der_public_key = load_der_public_key(public_key, backend=default_backend())
        uncompressed_public_key = der_public_key.public_bytes(
            encoding=serialization.Encoding.X962,
            format=serialization.PublicFormat.UncompressedPoint,
        )[1:]

    else:
        uncompressed_public_key = public_key[-64:]

    return PublicKey(uncompressed_public_key).to_canonical_address()
