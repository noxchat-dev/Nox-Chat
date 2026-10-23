
import asyncio
import base64
import json
from datetime import datetime
from websockets.asyncio.client import connect
from websockets.exceptions import ConnectionClosed
from prompt_toolkit import PromptSession
from prompt_toolkit.patch_stdout import patch_stdout
from prompt_toolkit import print_formatted_text
from prompt_toolkit.formatted_text import ANSI
from noxchat.crypto import encrypt_message, decrypt_message
from noxchat.protocol import encode_message
from noxchat.key import load_key


SERVER_URI = "ws://127.0.0.1:8765"
RESET = "\033[0m"


def terminal_color(hex_color):
    """Convertit une couleur hexadécimale en couleur ANSI."""
    hex_color = hex_color.lstrip("#")

    if len(hex_color) != 6:
        return "\033[37m"

    try:
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
    except ValueError:
        return "\033[37m"

    return f"\033[38;2;{r};{g};{b}m"


def current_timestamp():
    """Renvoie la date et l'heure au format NOXCHAT."""
    return datetime.now().strftime("%d/%m/%y  %H:%M")


async def receive_messages(ws, key):
    """Reçoit les messages du chat et les notifications système."""

    async for raw_message in ws:
        try:
            # Décodage JSON : les notifications système
            # n'ont pas nécessairement de champ payload.
            packet = json.loads(raw_message)

            if not isinstance(packet, dict):
                continue

            packet_type = packet.get("type")

            # Notifications système

            if packet_type == "system":
                event = packet.get("event")
                timestamp = current_timestamp()


                if event == "join":
                    username = packet.get("username", "Inconnu")
                    print(
                        f"\r\n[{timestamp}] [SYSTEM] -> "
                        f"{username} a rejoint le groupe.\n",
                        end="",
                        flush=True,
                    )

                elif event == "leave":
                    username = packet.get("username", "Inconnu")
                    color = packet.get("color", "#FFFFFF")
                    username_color = terminal_color(color)

                    with patch_stdout():
                        print_formatted_text(
                            ANSI(
                                f"\r\n[{timestamp}] [SYSTEM] -> "
                                f"{username_color}{username}{RESET} "
                                f"a quitté le groupe.\n"
                            ),
                            end="",
                        )

                elif event == "private_sent":
                    recipient = packet.get("recipient", "Inconnu")
                    print(
                        f"\r\n[NOXCHAT] Message privé envoyé à "
                        f"{recipient}.\n",
                        end="",
                        flush=True,
                    )

                elif event == "users":
                    users = packet.get("users", [])
                    print(
                        f"\r\n[NOXCHAT] Utilisateurs connectés "
                        f"({len(users)}) :",
                        flush=True,
                    )
                    for username in users:
                        print(f"  - {username}", flush=True)

                elif event == "help":
                    commands = packet.get("commands", [])
                    print("\r\n[NOXCHAT] Commandes disponibles :")
                    for command in commands:
                        print(
                            f"  {command['name']:<10} "
                            f"- {command['description']}"
                        )

                elif event == "error":
                    message = packet.get("message", "Erreur inconnue.")
                    print(f"\r\n[NOXCHAT] {message}", flush=True)


                continue


            # Ignorer les paquets qui ne sont pas des messages.

            # Vérifier et déchiffrer le message reçu.
            encrypted = base64.b64decode(
                packet["payload"],
                validate=True,
            )


            # Recevoir et déchiffrer les messages privés.
            if packet_type == "private":
                encrypted = base64.b64decode(
                    packet["payload"],
                    validate=True,
                )

                message = decrypt_message(key, encrypted)

                username = packet.get("username", "Inconnu")
                color = packet.get("color", "#FFFFFF")
                username_color = terminal_color(color)
                timestamp = current_timestamp()

                with patch_stdout():
                    print_formatted_text(
                        ANSI(
                            f"[{timestamp}] [PRIVÉ] "
                            f"{username_color}{username}{RESET} -> "
                            f"{message}"
                        )
                    )

                continue

            # Ignorer les autres types de paquets.
            if packet_type != "chat":
                continue

            message = decrypt_message(key, encrypted)

            username = packet.get("username", "Inconnu")
            color = packet.get("color", "#FFFFFF")
            username_color = terminal_color(color)
            timestamp = current_timestamp()


            with patch_stdout():
                print_formatted_text(
                    ANSI(
                        f"[{timestamp}] "
                        f"{username_color}{username}{RESET} -> {message}"
                    )
                )

        except (json.JSONDecodeError, KeyError, ValueError, TypeError):
            print(
                "\n[ERREUR] Message invalide ou impossible à déchiffrer.",
                flush=True,
            )
        except Exception as error:
            print(
                f"\n[ERREUR] Réception du message : {error}",
                flush=True,
            )


async def send_messages(ws, key):
    """Chiffre et envoie les messages saisis par l'utilisateur."""

    session = PromptSession()

    while True:
        with patch_stdout():
            message = await session.prompt_async(" ❯ ")


        if message.strip().lower() == "/quit":
            await ws.close()
            return


        # Commande pour envoyer un message privé
        if message.strip().lower().startswith("/msg "):
            parts = message.strip().split(maxsplit=2)

            if len(parts) < 3:
                print(
                    "[NOXCHAT] Utilisation : "
                    "/msg pseudo ton message"
                )
                continue

            recipient = parts[1]
            private_text = parts[2]

            try:
                encrypted = encrypt_message(key, private_text)
                payload = base64.b64encode(encrypted).decode("ascii")

                packet = json.dumps({
                    "type": "private",
                    "recipient": recipient,
                    "payload": payload,
                })

                await ws.send(packet)

            except ConnectionClosed:
                print("\n[NOXCHAT] Connexion fermée.")
                return

            continue


        # Commande locale pour nettoyer le terminal
        if message.strip().lower() == "/clear":
            print("\033[2J\033[H", end="", flush=True)
            continue

        # Autres commandes du serveur
        if message.strip().startswith("/"):
            packet = encode_message("command", message.strip())
            await ws.send(packet)
            continue

        if not message.strip():
            continue

        try:
            encrypted = encrypt_message(key, message)
            payload = base64.b64encode(encrypted).decode("ascii")
            packet = encode_message("chat", payload)

            await ws.send(packet)

        except ConnectionClosed:
            print("\n[NOXCHAT] Connexion fermée.")
            return


async def main():
    username = input("Choisis ton pseudo NOXCHAT : ").strip()

    if not username or len(username) > 24:
        print(
            "[ERREUR] Le pseudo doit contenir entre 1 et 24 caractères."
        )
        return

    key = load_key()

    print("\n[NOXCHAT] Connexion au serveur...")

    try:
        async with connect(SERVER_URI) as ws:
            # Présenter le pseudo au serveur.
            await ws.send(
                json.dumps({
                    "type": "hello",
                    "username": username,
                })
            )

            # Attendre la confirmation du serveur.
            raw_welcome = await asyncio.wait_for(
                ws.recv(),
                timeout=5,
            )

            welcome = json.loads(raw_welcome)

            if welcome.get("type") != "welcome":
                print("[ERREUR] Identification refusée.")
                return

            color = welcome.get("color", "#FFFFFF")
            username_color = terminal_color(color)

            # Nettoyer le terminal après la connexion.
            print("\033[2J\033[H", end="", flush=True)

            print(
                f"NOXCHAT — Connecté comme "
                f"{username_color}{username}{RESET}"
            )
            print("Tape /quit pour quitter.\n")
            print("Tape /quit pour quitter.\n")

            receiver = asyncio.create_task(
                receive_messages(ws, key)
            )

            try:
                await send_messages(ws, key)

            finally:
                receiver.cancel()
                await asyncio.gather(
                    receiver,
                    return_exceptions=True,
                )

    except asyncio.TimeoutError:
        print("[ERREUR] Le serveur n'a pas répondu à temps.")

    except ConnectionClosed as error:
        reason = getattr(error, "reason", "")
        print(
            f"[ERREUR] Connexion fermée par le serveur. {reason}"
        )

    except OSError:
        print(
            "[ERREUR] Serveur inaccessible. "
            "Vérifie qu'il est démarré."
        )

    except (json.JSONDecodeError, KeyError, ValueError) as error:
        print(f"[ERREUR] Réponse du serveur invalide : {error}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[NOXCHAT] Déconnexion.")

