import pytest

from eth_hub.aws.boto3_wrappers.exceptions import CantCreateKeyObjectAwsError, CantListAliasesAwsError, \
    CantGetAddressAwsError, CantListKeysAwsError
from eth_hub.aws.exceptions import CantGetKeyInfoError, CantListKeysError
from eth_hub.aws.key_store import AwsKeyStore
from .aws_mock import AwsMock, Key


def test_get_key(
        mocked_key: Key,
        key_manager: AwsKeyStore,
        aws_mock_with_key: AwsMock,
) -> None:
    # when
    key_manager.get_key(mocked_key.id)

    # then
    aws_mock_with_key.get_key_metadata_mock.assert_called_once()
    aws_mock_with_key.get_aliases_mock.assert_called_once()
    aws_mock_with_key.get_address_mock.assert_called_once()
    aws_mock_with_key.get_key_ids_mock.assert_not_called()


def test_get_key_with_exception_on_getting_metadata(
        mocked_key: Key,
        key_manager: AwsKeyStore,
        aws_mock_with_key: AwsMock,
) -> None:
    # given
    aws_mock_with_key.get_key_metadata_mock.side_effect = CantCreateKeyObjectAwsError

    # when / then
    with pytest.raises(CantGetKeyInfoError):
        key_manager.get_key(mocked_key.id)


def test_get_key_with_exception_on_getting_aliases(
        mocked_key: Key,
        key_manager: AwsKeyStore,
        aws_mock_with_key: AwsMock,
) -> None:
    # given
    aws_mock_with_key.get_aliases_mock.side_effect = CantListAliasesAwsError

    # when / then
    with pytest.raises(CantGetKeyInfoError):
        key_manager.get_key(mocked_key.id)


def test_get_key_with_exception_on_getting_addresses(
        mocked_key: Key,
        key_manager: AwsKeyStore,
        aws_mock_with_key: AwsMock,
) -> None:
    # given
    aws_mock_with_key.get_address_mock.side_effect = CantGetAddressAwsError

    # when / then
    with pytest.raises(CantGetKeyInfoError):
        key_manager.get_key(mocked_key.id)


def test_list_keys(
        key_manager: AwsKeyStore,
        aws_mock_with_key: AwsMock,
) -> None:
    # when
    keys = key_manager.list_keys()

    # then
    assert len(keys) == 1
    aws_mock_with_key.get_key_metadata_mock.assert_called_once()
    aws_mock_with_key.get_aliases_mock.assert_called_once()
    aws_mock_with_key.get_address_mock.assert_called_once()
    aws_mock_with_key.get_key_ids_mock.assert_called_once()


def test_list_keys_with_exception_on_getting_ids(
        key_manager: AwsKeyStore,
        aws_mock_with_key: AwsMock,
) -> None:
    # given
    aws_mock_with_key.get_key_ids_mock.side_effect = CantListKeysAwsError

    # when / then
    with pytest.raises(CantListKeysError):
        key_manager.list_keys()
