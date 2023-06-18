from hashlib import md5
from random import randint

def hashFilename(filename: str):
    random_suffix = str(randint(1, 1000000))
    
    hash_object = md5(random_suffix.encode())
    unique_hash = hash_object.hexdigest()

    return unique_hash