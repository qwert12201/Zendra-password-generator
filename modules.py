import hashlib
import sys
import os

algorithms = ["sha512", "md5", "sha256", "sha1"]

def hashlib_user(string: str, algorithm) -> str:
    return hashlib.new(algorithm, string.encode()).hexdigest()

def resource_path(path: str) -> str:
    if hasattr(sys, "_MEIPASS"):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, path)
