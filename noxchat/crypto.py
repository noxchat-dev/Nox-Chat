import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def generate_key() -> bytes:
    """Génère une clé AES de 256 bits."""
    return AESGCM.generate_key(bit_length=256)


def encrypt_message(key: bytes, plaintext: str) -> bytes:
    """Chiffre un message et renvoie le nonce suivi du texte chiffré."""
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)

    ciphertext = aesgcm.encrypt(
        nonce,
        plaintext.encode("utf-8"),
        None
    )

    return nonce + ciphertext


def decrypt_message(key: bytes, encrypted_message: bytes) -> str:
    """Déchiffre un message et vérifie son authenticité."""
    if len(encrypted_message) < 28:
        raise ValueError("Message chiffré invalide.")

    nonce = encrypted_message[:12]
    ciphertext = encrypted_message[12:]

    aesgcm = AESGCM(key)
    plaintext = aesgcm.decrypt(nonce, ciphertext, None)

    return plaintext.decode("utf-8")
