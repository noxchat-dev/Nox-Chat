import asyncio
from websockets.asyncio.client import connect


async def main():
    async with connect("ws://127.0.0.1:8765") as ws:
        print("Connexion WebSocket réussie !")


asyncio.run(main())
