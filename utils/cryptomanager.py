from cryptography.fernet import Fernet
import os


class CryptoManager:
    def __init__(self, key_file="secret.key"):
        self.key_file = key_file
        self.key = self.load_or_generate_key()

    def load_or_generate_key(self):
        if os.path.exists(self.key_file):
            with open(self.key_file, "rb") as key_file:
                key = key_file.read()
                print(
                    f"Key loaded: {key[:5]}..."
                )  # Show part of the key for verification
                return key
        else:
            key = Fernet.generate_key()
            with open(self.key_file, "wb") as key_file:
                key_file.write(key)
            print(
                f"New key generated: {key[:10]}..."
            )  # Show part of the key for verification
            return key

    def generate_key(self):
        key = Fernet.generate_key()
        with open(self.key_file, "wb") as key_file:
            key_file.write(key)
        return key

    def encrypt_message(self, message):
        f = Fernet(self.key)
        encrypted_message = f.encrypt(message.encode())
        return encrypted_message.decode()

    def decrypt_message(self, encrypted_message):
        try:
            f = Fernet(self.key)
            decrypted_message = f.decrypt(encrypted_message)
            return decrypted_message.decode()
        except Exception as e:
            print(f"Error decrypting message: {e}")
            raise e
