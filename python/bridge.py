# Web socket server
import asyncio
import json
import websockets

clients = set()

async def handler(websocket):
    clients.add(websocket)

    try:
        async for message in websocket:
            data = json.loads(message)
            print(data)

            # forward to clients
            for client in clients:
                if client != websocket:
                    await client.send(json.dumps(data))

    except websockets.ConnectionClosed:
        pass
    
    finally:
        clients.remove(websocket)

async def main():
    async with websockets.serve(handler, "localhost", 8765):
        print("Listening on localhost:8765")
        await asyncio.Future()

asyncio.run(main())