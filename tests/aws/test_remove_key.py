import pytest

from eth_hub.aws.boto3_wrappers.exceptions import CantDeleteKeyAwsError
from eth_hub.aws.exceptions import CantRemoveKey
from eth_hub.aws.key_store import AwsKeyStore
from .aws_mock import AwsMock, Key


def test_remove_key(
        key_manager: AwsKeyStore,
        mocked_key: Key,
        aws_mock_with_key: AwsMock,
) -> None:
    # when
    key_manager.remove_key(mocked_key.id)

    # then
    aws_mock_with_key.schedule_key_deletion_mock.assert_called_once()


def test_remove_key_with_exception(
        key_manager: AwsKeyStore,
        mocked_key: Key,
        aws_mock_with_key: AwsMock,
) -> None:
    # given
    aws_mock_with_key.schedule_key_deletion_mock.side_effect = CantDeleteKeyAwsError

    # when / then
    with pytest.raises(CantRemoveKey):
        key_manager.remove_key(mocked_key.id)
