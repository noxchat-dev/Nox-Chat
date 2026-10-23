import base64
from pathlib import Path

from noxchat.crypto import generate_key

KEY_FILE = Path(__file__).resolve().parent.parent / ".noxchat.key"


def load_key() -> bytes:
    """Charge la clé existante ou en crée une si nécessaire."""
    if not KEY_FILE.exists():
        key = generate_key()
        encoded_key = base64.b64encode(key)
        KEY_FILE.write_bytes(encoded_key)
        KEY_FILE.chmod(0o600)

    encoded_key = KEY_FILE.read_bytes()
    key = base64.b64decode(encoded_key, validate=True)

    if len(key) != 32:
        raise ValueError("La clé NOXCHAT doit contenir 32 octets.")

    return key
