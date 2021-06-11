import os.path
import re
from shared.crypto_util import crypto
from shared.crypto_util.crypto_class import Crypto


def test_encrypt_message_using_class():
    # Arrange :
    crypto = Crypto(secretFile="config/crypto_secret.key")
    message = "some secret message"

    # Act :
    encrypted = crypto.encrypt_message(message)
    decrypted = crypto.decrypt_message(encrypted)

    # Assert :
    assert decrypted == message
    # assert re.match(r"^\w+", encrypted)

def test_encrypt_file_using_class():
    # Arrange :
    crypto = Crypto(secretFile="config/crypto_secret.key")

    # Act :
    crypto.encrypt_file(filename="config/crypto_secret.key")

    # Assert :
    assert os.path.isfile("config/crypto_secret.key.encrypted")


def test_decrypt_file_using_class():
    # Arrange :
    crypto = Crypto(secretFile="config/crypto_secret.key")

    crypto.encrypt_file(filename="config/crypto_secret.key")

    # Act :
    crypto.decrypt_file(filename="config/crypto_secret.key.encrypted")

    # Assert :
    assert os.path.isfile("config/crypto_secret.key.encrypted.decrypted")
