import asyncio
from websockets.asyncio.client import connect


async def main():
    uri = "ws://127.0.0.1:8765"

    async with connect(uri) as client_a:
        async with connect(uri) as client_b:
            print("Deux clients connectés.")

            await client_a.send("Bonjour depuis NOXCHAT !")
            message = await asyncio.wait_for(
                client_b.recv(),
                timeout=5
            )

            print(f"Client B reçoit : {message}")


asyncio.run(main())
