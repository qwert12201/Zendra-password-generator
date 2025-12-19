import base64
import hashlib
import binascii

from cryptography.fernet import Fernet

algorithms = ["sha512", "md5", "sha256", "sha1"]

def hashlib_user(string: str, algorithm) -> str:
    return hashlib.new(algorithm, string.encode()).hexdigest()
