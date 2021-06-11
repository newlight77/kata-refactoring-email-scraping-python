import pytest


@pytest.fixture
def mock_crypto(mocker):
    mock_crypto = mocker.patch(
        "shared.crypto_util.Crypto"
    )

    return mock_crypto
