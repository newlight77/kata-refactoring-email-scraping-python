from cryptography.fernet import Fernet
import os.path

def get_or_generate_key(secretFile="config/crypto_secret.key"):
    """
    Generates a key and save it into a file
    """
    if not os.path.isfile(secretFile):
        key = Fernet.generate_key()
        with open(secretFile, "wb") as key_file:
            key_file.write(key)
            
    return open(secretFile, "rb").read()


def load_key(secretFile="config/crypto_secret.key"):
    """
    Load the previously generated key
    """
    return open(secretFile, "rb").read()

def encrypt_message(message, key):
    """
    Encrypts a message
    """
    encoded_message = message.encode()
    f = Fernet(key)
    encrypted_message = f.encrypt(encoded_message)

    return encrypted_message

def decrypt_message(encrypted_message, key):
    """
    Decrypts an encrypted message
    """
    f = Fernet(key)
    decrypted_message = f.decrypt(encrypted_message)

    return decrypted_message.decode()

def encrypt_file(filename, key):
    """
    Given a filename (str) and key (bytes), it encrypts the file and write it
    """
    f = Fernet(key)
    
    with open(filename, "rb") as file:
        # read all file data
        file_data = file.read()
        
    # encrypt data
    encrypted_data = f.encrypt(file_data)
        
    # write the encrypted file
    with open(f"{filename}.encrypted", "wb") as file:
        file.write(encrypted_data)


def decrypt_file(filename, key):
    """
    Given a filename (str) and key (bytes), it decrypts the file and write it
    """
    f = Fernet(key)
    with open(filename, "rb") as file:
        # read the encrypted data
        encrypted_data = file.read()
        
    # decrypt data
    decrypted_data = f.decrypt(encrypted_data)
    
    # write the original file
    with open(f"{filename}.decrypted", "wb") as file:
        file.write(decrypted_data)