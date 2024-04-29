from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad


def encrypt_AES(key, data):
    cipher = AES.new(key, AES.MODE_CBC)
    ct_bytes = cipher.encrypt(pad(data.encode(), AES.block_size))
    iv = cipher.iv
    return iv + ct_bytes


def decrypt_AES(key, cipher_text):
    iv = cipher_text[: AES.block_size]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    pt_bytes = cipher.decrypt(cipher_text[AES.block_size :])
    return unpad(pt_bytes, AES.block_size).decode()


# Example usage:
data = "Hello, AES encryption2!"
key = get_random_bytes(32)  # 256-bit key
cipher_text = encrypt_AES(key, data)
print("Cipher text:", cipher_text)

decrypted_data = decrypt_AES(key, cipher_text)
print("Decrypted:", decrypted_data)
