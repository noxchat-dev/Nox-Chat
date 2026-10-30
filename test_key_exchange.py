from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    PublicFormat,
)
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes

# Simulation de deux appareils indépendants
alice_private = X25519PrivateKey.generate()
bob_private = X25519PrivateKey.generate()

alice_public = alice_private.public_key()
bob_public = bob_private.public_key()

# Échange simulé des clés publiques
alice_public_bytes = alice_public.public_bytes(
    Encoding.Raw, PublicFormat.Raw
)
bob_public_bytes = bob_public.public_bytes(
    Encoding.Raw, PublicFormat.Raw
)

# Chaque appareil calcule le même secret partagé
alice_shared = alice_private.exchange(bob_public)
bob_shared = bob_private.exchange(alice_public)

assert alice_shared == bob_shared

# Dérivation d'une clé de session avec HKDF
def derive_session_key(shared_secret):
    return HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=b"NOXCHAT session v1",
    ).derive(shared_secret)

alice_session_key = derive_session_key(alice_shared)
bob_session_key = derive_session_key(bob_shared)

assert alice_session_key == bob_session_key

print("Clés publiques échangées :", len(alice_public_bytes), "et", len(bob_public_bytes), "octets")
print("Secret partagé identique : OUI")
print("Clé de session identique : OUI")
print("TEST D'ACCORD DE CLÉ RÉUSSI")
