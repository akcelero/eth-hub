from typing import Generator

import pytest
from botocore.stub import Stubber
from mypy_boto3_kms import KMSClient


@pytest.fixture
def stubber(client: KMSClient) -> Generator[Stubber, None, None]:
    stubber = Stubber(client)
    stubber.activate()

    yield stubber

    stubber.deactivate()
