import hashlib

algorithms = ["sha512", "md5", "sha256", "sha1"]

def hashlib_user(string: str, algorithm) -> str:
    return hashlib.new(algorithm, string.encode()).hexdigest()

def type_of_bit(bits: int | float) -> str:
    bytess = bits / 8
    data = {"БИТ": bits, "БАЙТ": bytess, "КБ": bytess / 1024, "МБ": bytess / 1048576, "ГБ": bytess / 1048576 / 1024, "ТБ": bytess / 1099511627776}
    for key, value in data.items():
        if value >= 1:
            result = str(round(value, 2)) + " " + key
    return result
