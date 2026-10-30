import argparse
import asyncio
import json
import secrets
from datetime import datetime

import websockets
from websockets.asyncio.server import serve

HOST = "127.0.0.1"
PORT = 8765
MAX_CLIENTS = 50


def timestamp():
    """Retourne la date et l'heure locales avec les millisecondes."""
    return datetime.now().strftime("%d/%m/%Y %H:%M:%S.%f")[:-3]


COLORS = [
    "#B6FF4A", "#45C8FF", "#FF426D", "#B388FF",
    "#FFB86C", "#50FA7B", "#8BE9FD", "#FF79C6",
    "#F1FA8C", "#BD93F9", "#00E5FF", "#FF6E6E",
    "#A3FF12", "#FFA6C9", "#7DF9FF", "#E0AAFF",
    "#FFD166", "#06D6A0", "#EF476F", "#118AB2",
    "#C1FBA4", "#F7A072", "#A0C4FF", "#CAFFBF",
    "#FFC6FF", "#9BF6FF",
]

clients = {}
used_colors = {}


def assign_color():
    """Attribue une couleur parmi les moins utilisées."""
    counts = {color: 0 for color in COLORS}

    for color in used_colors.values():
        if color in counts:
            counts[color] += 1

    least_used = min(counts.values())
    available = [
        color for color, count in counts.items()
        if count == least_used
    ]

    return secrets.choice(available)


async def send_system(websocket, event, **data):
    """Envoie une notification système à un client."""
    packet = {
        "type": "system",
        "event": event,
        **data,
    }
    await websocket.send(json.dumps(packet))


async def broadcast_system(event, **data):
    """Diffuse une notification système aux clients connectés."""
    packet = json.dumps({
        "type": "system",
        "event": event,
        **data,
    })

    for client in list(clients):
        try:
            await client.send(packet)
        except websockets.ConnectionClosed:
            pass


async def handler(websocket):
    username = None

    try:
        # Identification du client.
        raw = await asyncio.wait_for(websocket.recv(), timeout=15)
        request = json.loads(raw)

        if not isinstance(request, dict):
            await websocket.close(
                code=1008, reason="Identification invalide"
            )
            return

        if request.get("type") != "hello":
            await websocket.close(
                code=1008, reason="Identification requise"
            )
            return

        username = request.get("username", "")

        if not isinstance(username, str):
            await websocket.close(
                code=1008, reason="Pseudo invalide"
            )
            return

        username = username.strip()

        if not username or len(username) > 24:
            await websocket.close(
                code=1008, reason="Pseudo invalide"
            )
            return
        
        if len(clients) >= MAX_CLIENTS:
            await websocket.close(
                code=1013,
                reason="Serveur complet : maximum 50 utilisateurs."
            )
            return

        active_names = {
            info["username"].casefold()
            for info in clients.values()
        }

        if username.casefold() in active_names:
            await websocket.close(
                code=1008, reason="Pseudo déjà utilisé"
            )
            return

        color = assign_color()
        user_id = secrets.token_hex(8)

        clients[websocket] = {
            "id": user_id,
            "username": username,
            "color": color,
        }
        used_colors[user_id] = color

        await websocket.send(json.dumps({
            "type": "welcome",
            "id": user_id,
            "username": username,
            "color": color,
        }))

        print(
            f"[{timestamp()}] [+] {username} connecté ({color}). "
            f"Total : {len(clients)}"
        )
        await broadcast_system("join", username=username)

        async for raw_message in websocket:
            try:
                packet = json.loads(raw_message)
            except (json.JSONDecodeError, TypeError):
                await send_system(
                    websocket, "error",
                    message="Paquet JSON invalide."
                )
                continue

            if not isinstance(packet, dict):
                await send_system(
                    websocket, "error",
                    message="Format de paquet invalide."
                )
                continue

            packet_type = packet.get("type")

            # Commandes gérées par le serveur.
            if packet_type == "command":
                command = packet.get("payload", "")

                if not isinstance(command, str):
                    await send_system(
                        websocket, "error",
                        message="Commande invalide."
                    )
                    continue

                parts = command.strip().split()
                command_name = parts[0].lower() if parts else ""

                if command_name == "/users":
                    if len(parts) != 1:
                        await send_system(
                            websocket, "error",
                            message="Utilisation : /users"
                        )
                        continue

                    user_list = [
                        info["username"]
                        for info in clients.values()
                    ]

                    await send_system(
                        websocket, "users",
                        users=user_list
                    )

                elif command_name == "/help":
                    if len(parts) != 1:
                        await send_system(
                            websocket, "error",
                            message="Utilisation : /help"
                        )
                        continue

                    commands = [
                        {
                            "name": "/users",
                            "description": "Afficher les utilisateurs connectés",
                        },
                        {
                            "name": "/help",
                            "description": "Afficher les commandes disponibles",
                        },
                        {
                            "name": "/clear",
                            "description": "Nettoyer le terminal local",
                        },
                        {
                            "name": "/msg pseudo message",
                            "description": "Envoyer un message privé",
                        },
                        {
                            "name": "/quit",
                            "description": "Quitter NOXCHAT",
                        },
                    ]

                    await send_system(
                        websocket, "help",
                        commands=commands
                    )

                else:
                    await send_system(
                        websocket, "error",
                        message="Commande inconnue. Tape /help."
                    )

                continue

            # Message privé : le contenu reste chiffré.
            if packet_type == "private":
                recipient_name = packet.get("recipient")
                payload = packet.get("payload")

                if (
                    not isinstance(recipient_name, str)
                    or not recipient_name.strip()
                    or not isinstance(payload, str)
                    or not payload
                ):
                    await send_system(
                        websocket, "error",
                        message="Message privé invalide."
                    )
                    continue

                recipient_name = recipient_name.strip()

                recipient_socket = next(
                    (
                        client
                        for client, info in clients.items()
                        if info["username"].casefold()
                        == recipient_name.casefold()
                    ),
                    None,
                )

                if recipient_socket is None:
                    await send_system(
                        websocket, "error",
                        message=f"Utilisateur '{recipient_name}' introuvable."
                    )
                    continue

                if recipient_socket == websocket:
                    await send_system(
                        websocket, "error",
                        message="Tu ne peux pas t'envoyer un message privé."
                    )
                    continue

                outgoing = json.dumps({
                    "type": "private",
                    "sender_id": user_id,
                    "username": username,
                    "color": color,
                    "payload": payload,
                })

                try:
                    await recipient_socket.send(outgoing)
                except websockets.ConnectionClosed:
                    await send_system(
                        websocket, "error",
                        message="Le destinataire s'est déconnecté."
                    )
                    continue

                await send_system(
                    websocket, "private_sent",
                    recipient=recipient_name
                )
                continue

            # Message de chat public.
            if packet_type == "chat":
                payload = packet.get("payload")

                if not isinstance(payload, str) or not payload:
                    await send_system(
                        websocket, "error",
                        message="Message public invalide."
                    )
                    continue

                outgoing = json.dumps({
                    "type": "chat",
                    "sender_id": user_id,
                    "username": username,
                    "color": color,
                    "payload": payload,
                })

                for client in list(clients):
                    if client == websocket:
                        continue

                    try:
                        await client.send(outgoing)
                    except websockets.ConnectionClosed:
                        pass

                continue

            await send_system(
                websocket, "error",
                message="Type de paquet inconnu."
            )

    except websockets.ConnectionClosed:
        pass
    except asyncio.TimeoutError:
        pass
    except (json.JSONDecodeError, TypeError):
        try:
            await websocket.close(
                code=1008, reason="Protocole invalide"
            )
        except websockets.ConnectionClosed:
            pass
    finally:
        info = clients.pop(websocket, None)

        if info:
            used_colors.pop(info["id"], None)

            print(
                f"[{timestamp()}] [-] {info['username']} déconnecté. "
                f"Total : {len(clients)}"
            )
            await broadcast_system(
                "leave",
                username=info["username"],
                color=info["color"],
            )

async def main(host, port):
    async with serve(handler, host, port):
        print(f"[NOXCHAT] Serveur actif sur ws://{host}:{port}")
        await asyncio.Future()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Serveur NOXCHAT")
    parser.add_argument("--host", default=HOST, help="Adresse d'écoute")
    parser.add_argument("--port", type=int, default=PORT, help="Port d'écoute")
    args = parser.parse_args()

    try:
        asyncio.run(main(args.host, args.port))
    except KeyboardInterrupt:
        print("\n[NOXCHAT] Serveur arrêté.")
