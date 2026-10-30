from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from noxchat.identity import generate_identity


def derive_session_key(shared_secret):
    return HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=b"NOXCHAT session v1",
    ).derive(shared_secret)


def main():
    # Simulation de deux appareils.
    alice_private, alice_public = generate_identity()
    bob_private, bob_public = generate_identity()

    alice_secret = alice_private.exchange(bob_public)
    bob_secret = bob_private.exchange(alice_public)

    alice_key = derive_session_key(alice_secret)
    bob_key = derive_session_key(bob_secret)

    assert alice_key == bob_key

    # Alice chiffre un message avec la clé de session.
    message = "Bonjour depuis Alice !"
    nonce = AESGCM.generate_key(bit_length=128)[:12]
    ciphertext = AESGCM(alice_key).encrypt(
        nonce, message.encode("utf-8"), None
    )

    # Bob le déchiffre avec sa clé de session.
    decrypted = AESGCM(bob_key).decrypt(
        nonce, ciphertext, None
    ).decode("utf-8")

    assert decrypted == message

    print("Clé de session commune : OK")
    print("Chiffrement AES-GCM : OK")
    print("Déchiffrement par l'autre appareil : OK")
    print("TEST RÉUSSI")


if __name__ == "__main__":
    main()
