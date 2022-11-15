import hashlib

password = 'Hello_World!'

hashed = hashlib.sha256(password.encode('utf-8')).hexdigest()

print(hashed)
