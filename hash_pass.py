import hashlib

def hash_password(password):
    i=0
    while i <314:                                                           #rehasht den Sting 314x
        i+=1
        password=hashlib.sha512(str(password).encode("utf-8")).hexdigest()  #generiert mit sha512, den Hash
    print(password+"hi")
    return (password)                                                         #gibt den Hash zurück