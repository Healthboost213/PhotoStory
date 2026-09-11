from cryptography.hazmat.primitives.ciphers.aead import AESGCM
print(AESGCM.generate_key(256).hex())