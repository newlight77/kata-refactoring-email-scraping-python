import pytest
import os.path
import re
from shared.crypto_util import crypto
from shared.crypto_util.crypto_class import Crypto

@pytest.fixture(autouse=True)
def run_before_and_after_tests():
    """Fixture to execute asserts before and after a test is run"""
    # Setup

    yield  # this is where the testing happens

    # Teardown
    if(os.path.isfile("config/crypto_secret.key.encrypted")):
        os.remove("config/crypto_secret.key.encrypted")
    if(os.path.isfile("config/crypto_secret.key.encrypted.decrypted")):
        os.remove("config/crypto_secret.key.encrypted.decrypted")

def test_encrypt_message():
    # Arrange :
    key = crypto.get_or_generate_key()
    message = "some secret message"

    # Act :
    encrypted = crypto.encrypt_message(message, key)
    decrypted = crypto.decrypt_message(encrypted, key)

    # Assert :
    assert decrypted == message
    # assert re.match(r"^\w+", encrypted)


def test_encrypt_file():
    # Arrange :
    key = crypto.get_or_generate_key()

    # Act :
    crypto.encrypt_file(filename="config/crypto_secret.key", key=key)

    # Assert :
    assert os.path.isfile("config/crypto_secret.key.encrypted")


def test_decrypt_file():
    # Arrange :
    key = crypto.get_or_generate_key()
    crypto.encrypt_file(filename="config/crypto_secret.key", key=key)

    # Act :
    crypto.decrypt_file(filename="config/crypto_secret.key.encrypted", key=key)

    # Assert :
    assert os.path.isfile("config/crypto_secret.key.encrypted.decrypted")
