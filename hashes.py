import hashlib

algorithms = ["sha512", "md5", "sha256", "sha1"]

def hashlib_user(string: str, algorithm) -> str:
    return hashlib.new(algorithm, string.encode()).hexdigest()
