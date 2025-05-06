import pytest

from eth_hub.aws.boto3_wrappers.exceptions import CantCreateKeyObjectAwsError
from eth_hub.aws.exceptions import CantSetAlias, AliasAlreadyTakenError
from eth_hub.aws.key_store import AwsKeyStore
from .aws_mock import AwsMock, Key


def test_set_alias(
        mocked_key: Key,
        key_manager: AwsKeyStore,
        aws_mock_with_key: AwsMock,
) -> None:
    # given
    alias = "test"

    # when
    key_manager.set_alias(mocked_key.id, alias)

    # then
    aws_mock_with_key.set_alias_mock.assert_called_once()
    assert alias in aws_mock_with_key.keys[mocked_key.id].aliases


def test_set_already_taken_alias(
        mocked_key: Key,
        key_manager: AwsKeyStore,
        aws_mock_with_key: AwsMock,
) -> None:
    # given
    alias = "test"
    mocked_key.aliases.append(alias)

    # when
    with pytest.raises(AliasAlreadyTakenError):
        key_manager.set_alias(mocked_key.id, alias)


def test_set_alias_with_exception(
        mocked_key: Key,
        key_manager: AwsKeyStore,
        aws_mock_with_key: AwsMock,
) -> None:
    # given
    alias = "test"
    aws_mock_with_key.set_alias_mock.side_effect = CantCreateKeyObjectAwsError

    # when
    with pytest.raises(CantSetAlias):
        key_manager.set_alias(mocked_key.id, alias)
