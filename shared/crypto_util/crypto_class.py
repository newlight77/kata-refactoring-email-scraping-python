from cryptography.fernet import Fernet
import os.path


class Crypto():
    
    def __init__(self, secretFile="config/secret.key"):
        if not os.path.isfile(secretFile):
            self.key = Fernet.generate_key()
            with open(secretFile, "wb") as key_file:
                key_file.write(self.key)
        else:
            self.key = open(secretFile, "rb").read()
            
        self.fernet = Fernet(self.key)

    def encrypt_message(self, message):
        """
        Encrypts a message
        """
        return self.fernet.encrypt(message.encode())

    def decrypt_message(self, encrypted_message):
        """
        Decrypts an encrypted message
        """
        return self.fernet.decrypt(encrypted_message).decode()

    def encrypt_file(self, filename):
        """
        Given a filename (str) and key (bytes), it encrypts the file and write it
        """
        
        with open(filename, "rb") as file:
            # read all file data
            file_data = file.read()
        
        # encrypt data
        encrypted_data = self.fernet.encrypt(file_data)
            
        # write the encrypted file
        with open(f"{filename}.encrypted", "wb") as file:
            file.write(encrypted_data)


    def decrypt_file(self, filename):
        """
        Given a filename (str) and key (bytes), it decrypts the file and write it
        """
        with open(filename, "rb") as file:
            # read the encrypted data
            encrypted_data = file.read()
        
        # decrypt data
        decrypted_data = self.fernet.decrypt(encrypted_data)
        
        # write the original file
        with open(f"{filename}.decrypted", "wb") as file:
            file.write(decrypted_data)