
import asyncio
import json

from websockets.asyncio.client import connect
from websockets.exceptions import ConnectionClosed


SERVER_URI = "ws://127.0.0.1:8765"
MAX_CLIENTS = 50
TIMEOUT = 5


async def open_client(number):
    ws = await connect(SERVER_URI)

    try:
        await ws.send(json.dumps({
            "type": "hello",
            "username": f"capacity_test_{number:02d}",
        }))

        response = await asyncio.wait_for(
            ws.recv(),
            timeout=TIMEOUT,
        )
        packet = json.loads(response)

        if packet.get("type") == "welcome":
            return ws

        await ws.close()
        raise AssertionError(
            f"Client {number} refusé : réponse inattendue {packet}"
        )

    except BaseException:
        await ws.close()
        raise

async def test_capacity():
    connections = []
    extra = None

    try:
        # Test : les 50 premières connexions doivent réussir.
        for number in range(1, MAX_CLIENTS + 1):
            ws = await open_client(number)
            connections.append(ws)

        print(f"OK : les {MAX_CLIENTS} clients sont acceptés.")


        # Test : le client 51 doit être refusé avec le code 1013.
        extra = await connect(SERVER_URI)

        try:
            await extra.send(json.dumps({
                "type": "hello",
                "username": "capacity_test_extra",
            }))
        except ConnectionClosed:
            pass

        try:
            await asyncio.wait_for(
                extra.wait_closed(),
                timeout=TIMEOUT,
            )
        except asyncio.TimeoutError:
            raise AssertionError(
                "Le serveur n'a pas fermé la connexion du client 51."
            )

        if extra.close_code != 1013:
            raise AssertionError(
                f"Code attendu : 1013 ; code reçu : {extra.close_code}"
            )

        print("OK : le client 51 est refusé (code 1013).")
        print("SUCCÈS : tous les tests de capacité sont réussis.")

    finally:
        # Fermer le client supplémentaire, s'il a été créé.
        if extra is not None:
            await extra.close()

        # Fermer les clients de test en parallèle pour limiter l'attente.
        if connections:
            await asyncio.gather(
                *(ws.close() for ws in connections),
                return_exceptions=True,
            )

        print("Nettoyage des connexions de test terminé.")


if __name__ == "__main__":
    try:
        asyncio.run(test_capacity())
    except Exception as exc:
        print(f"ÉCHEC DU TEST : {exc}")
        raise SystemExit(1)
