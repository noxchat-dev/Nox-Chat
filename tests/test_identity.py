from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

from noxchat.identity import generate_identity, export_public_key


def derive_session_key(shared_secret):
    return HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=b"NOXCHAT session v1",
    ).derive(shared_secret)


def main():
    # Deux appareils avec des identités différentes.
    alice_private, alice_public = generate_identity()
    bob_private, bob_public = generate_identity()

    # Chaque appareil dérive le secret à partir de la clé publique de l'autre.
    alice_shared = alice_private.exchange(bob_public)
    bob_shared = bob_private.exchange(alice_public)

    assert export_public_key(alice_public) != export_public_key(bob_public)
    assert alice_shared == bob_shared

    alice_session = derive_session_key(alice_shared)
    bob_session = derive_session_key(bob_shared)

    assert alice_session == bob_session

    print("Identités distinctes : OK")
    print("Secret partagé identique : OK")
    print("Clé de session identique : OK")
    print("TEST RÉUSSI")


if __name__ == "__main__":
    main()
