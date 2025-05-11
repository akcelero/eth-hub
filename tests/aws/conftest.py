from uuid import uuid4

import boto3
import pytest
from eth_account import Account
from mypy_boto3_kms import KMSClient
from pytest_mock import MockerFixture

from eth_hub.aws.key_store import AwsKeyStore

from .aws_mock import AwsMock, Key


@pytest.fixture
def client() -> KMSClient:
    return boto3.client("kms", region_name="eu-west-2")


@pytest.fixture
def key_manager(client: KMSClient) -> AwsKeyStore:
    return AwsKeyStore(client)


@pytest.fixture
def aws_mock(mocker: MockerFixture) -> AwsMock:
    return AwsMock(mocker)


@pytest.fixture
def mocked_key() -> Key:
    return Key(
        id=uuid4(),
        address=Account.create().address,
    )


@pytest.fixture
def aws_mock_with_key(mocked_key: Key, aws_mock: AwsMock, client: KMSClient) -> AwsMock:
    aws_mock.keys[mocked_key.id] = mocked_key
    return aws_mock
