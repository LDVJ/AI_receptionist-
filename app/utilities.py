# hash  our password, generate slug
from pwdlib import PasswordHash
import uuid

hashing = PasswordHash.recommended()

def slug_generation(input : str) -> str:
    return input.strip().lower().replace(" ","-")

def create_hash_password(password : str) ->  str:
    return hashing.hash(password=password)

def verify_hash_password(original : str, hash_pwd : str) -> bool:
    return hashing.verify(password=original, hash=hash_pwd)

def generate_id():
    return uuid.uuid4().hex