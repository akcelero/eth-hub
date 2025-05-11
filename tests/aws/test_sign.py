from uuid import uuid4

from asn1crypto.algos import DSASignature

from eth_hub.aws.key_store import AwsKeyStore

from .aws_mock import AwsMock, Key


def test_sign_hash(
    key_manager: AwsKeyStore,
    mocked_key: Key,
    aws_mock: AwsMock,
) -> None:
    # given
    address = "0x707cd01a8fc30c503d10ccfb8fe0c6670817b814"
    r = 77499307603103543196277082859912786141927594951515498733161022132679134249953
    s = 52246846724921623538504070280221495554738823431252421718508664272925772355973
    v = 1

    key_id = uuid4()
    aws_mock.keys[key_id] = Key(id=key_id, address=address)
    aws_mock.dsa_signatures.append(DSASignature({"r": r, "s": s}))

    hash_ = bytes.fromhex(
        "fdca2948a3f973fdfd6e0574a1980793d8fa2f157ab9866937029c7efc69aca2"
    )

    # when
    signature = key_manager.sign_hash(key_id, hash_)

    # then
    assert signature.r == r
    assert signature.s == s
    assert signature.v == v
