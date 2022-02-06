import hashlib

def hash_password(hash):
    i=0
    while i <314:
        i+=1
        hash=hashlib.sha512(str(hash).encode("utf-8")).hexdigest()
    return hash