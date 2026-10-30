from noxchat.identity import generate_identity
from noxchat.session import derive_session_key


def main():
    # Générer deux identités indépendantes.
    alice_private, alice_public = generate_identity()
    bob_private, bob_public = generate_identity()

    # Chaque identité calcule le même secret partagé.
    alice_secret = alice_private.exchange(bob_public)
    bob_secret = bob_private.exchange(alice_public)

    # Dériver les clés de session.
    alice_key = derive_session_key(alice_secret)
    bob_key = derive_session_key(bob_secret)

    assert alice_key == bob_key
    assert len(alice_key) == 32

    print("Clé de session commune : OK")
    print("Longueur de 32 octets : OK")

    # Vérifier le rejet d'un secret invalide.
    try:
        derive_session_key(b"secret_invalide")
    except ValueError:
        print("Rejet du secret invalide : OK")
    else:
        raise AssertionError("Un secret invalide a été accepté.")

    print("TEST RÉUSSI")


if __name__ == "__main__":
    main()
