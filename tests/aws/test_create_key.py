import pytest

from eth_hub.aws.boto3_wrappers.exceptions import CantCreateKeyObjectAwsError, CantImportKeyMaterialAwsError
from eth_hub.aws.exceptions import CantCreateKeyError
from eth_hub.aws.key_store import AwsKeyStore
from .aws_mock import AwsMock


def test_create_key(
        key_manager: AwsKeyStore,
        aws_mock: AwsMock,
) -> None:
    # when
    key_manager.create_key()

    # then
    aws_mock.create_key_item_mock.assert_called_once()
    aws_mock.fulfil_private_key_mock.assert_not_called()


def test_create_key_with_exception(
        key_manager: AwsKeyStore,
        aws_mock: AwsMock,
) -> None:
    # given
    aws_mock.create_key_item_mock.side_effect = CantCreateKeyObjectAwsError

    # when / then
    with pytest.raises(CantCreateKeyError):
        key_manager.create_key()


def test_import_key(
        key_manager: AwsKeyStore,
        aws_mock: AwsMock,
) -> None:
    # given
    pk = bytes.fromhex("b8c0e2a59eb900206b21ad19b632725b0e113fb46cef49ed3d418cba056dbd00")

    # when
    key_manager.import_key(pk)

    # then
    aws_mock.create_key_item_mock.assert_called_once()
    aws_mock.fulfil_private_key_mock.assert_called_once()


def test_import_key_with_exception_on_key_creation(
        key_manager: AwsKeyStore,
        aws_mock: AwsMock,
) -> None:
    # given
    pk = bytes.fromhex("b8c0e2a59eb900206b21ad19b632725b0e113fb46cef49ed3d418cba056dbd00")
    aws_mock.create_key_item_mock.side_effect = CantCreateKeyObjectAwsError

    # when / then
    with pytest.raises(CantCreateKeyError):
        key_manager.import_key(pk)


def test_import_key_with_exception_on_fulfilling_pk(
        key_manager: AwsKeyStore,
        aws_mock: AwsMock,
) -> None:
    # given
    pk = bytes.fromhex("b8c0e2a59eb900206b21ad19b632725b0e113fb46cef49ed3d418cba056dbd00")
    aws_mock.fulfil_private_key_mock.side_effect = CantImportKeyMaterialAwsError

    # when / then
    with pytest.raises(CantCreateKeyError):
        key_manager.import_key(pk)
