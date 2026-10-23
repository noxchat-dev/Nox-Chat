from noxchat.crypto import (
    generate_key,
    encrypt_message,
    decrypt_message,
)


def main():
    key = generate_key()
    message = "Message secret de NOXCHAT"

    encrypted = encrypt_message(key, message)

    print("Message original :", message)
    print("Message chiffré :", encrypted.hex())

    decrypted = decrypt_message(key, encrypted)
    print("Message déchiffré :", decrypted)

    assert decrypted == message
    print("TEST RÉUSSI : chiffrement et déchiffrement corrects.")


if __name__ == "__main__":
    main()
