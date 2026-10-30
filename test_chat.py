import asyncio
import json
from websockets.asyncio.client import connect


async def main():
    uri = "ws://127.0.0.1:8765"

    async with connect(uri) as client_a:
        async with connect(uri) as client_b:
            await client_a.send(json.dumps({
                "type": "hello",
                "username": "Test_A",
            }))
            welcome_a = json.loads(await client_a.recv())

            await client_b.send(json.dumps({
                "type": "hello",
                "username": "Test_B",
            }))
            welcome_b = json.loads(await client_b.recv())

            if welcome_a.get("type") != "welcome":
                raise RuntimeError(f"Identification A échouée : {welcome_a}")
            if welcome_b.get("type") != "welcome":
                raise RuntimeError(f"Identification B échouée : {welcome_b}")

            print("Deux clients connectés.")

            test_message = "Bonjour depuis NOXCHAT !"
            await client_a.send(json.dumps({
                "type": "chat",
                "payload": test_message,
            }))

            while True:
                raw = await asyncio.wait_for(client_b.recv(), timeout=5)
                packet = json.loads(raw)
                if packet.get("type") == "chat":
                    break

            if packet.get("payload") != test_message:
                raise AssertionError(
                    f"Message inattendu : {packet.get('payload')!r}"
                )

            print(f"Client B reçoit : {packet['payload']}")
            print("TEST RÉUSSI : le serveur relaie le message.")


if __name__ == "__main__":
    asyncio.run(main())
