from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF


def derive_session_key(shared_secret: bytes) -> bytes:
    """Dérive une clé AES-256 à partir d'un secret X25519 partagé."""
    if not isinstance(shared_secret, bytes) or len(shared_secret) != 32:
        raise ValueError("Le secret partagé doit contenir 32 octets.")

    return HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=b"NOXCHAT session v1",
    ).derive(shared_secret)
