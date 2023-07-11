import base64
import uuid
import json

password = None
try:
    password = open(".pwd", "r").read()
except IOError:
    pass


def generate_salt():
    salt = str(uuid.uuid4())  # Generate a random UUID as the salt
    return salt


def generate_key(salt):
    key = str(uuid.uuid4())  # Generate a random UUID as the key
    return key


def get_salt_and_key():
    try:
        with open(".key", "r") as key_file:
            key_data = json.load(key_file)
            salt = key_data["salt"]
            key = key_data["key"]
    except (IOError, json.JSONDecodeError):
        salt = generate_salt()
        key = generate_key(salt)
        with open(".key", "w") as key_file:
            json.dump({"salt": salt, "key": key}, key_file)
    return salt, key


salt, key = get_salt_and_key()


def encode(string, key=key):
    encoded_bytes = []
    salt, k = get_salt_and_key() 
    string = string + salt #     Salting the password
    for i in range(len(string)):
        key_c = key[i % len(key)]
        encoded_byte = (ord(string[i]) + ord(key_c)) % 256
        encoded_bytes.append(encoded_byte)
    encoded_string = base64.urlsafe_b64encode(bytes(encoded_bytes)).decode()
    return encoded_string


def decode(string, key=key):
    decoded_bytes = base64.urlsafe_b64decode(string.encode())
    decoded_chars = []
    for i in range(len(decoded_bytes)):
        key_c = key[i % len(key)]
        decoded_char = chr((decoded_bytes[i] - ord(key_c)) % 256)
        decoded_chars.append(decoded_char)
    decoded_string = "".join(decoded_chars)
    decoded_string = decoded_string[: -len(salt)] #    Removing the salt from the decrypted password
    return decoded_string
