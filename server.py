# ~~~ SERVER code ~~~
# This will not be executed locally. This will be located on the cloud to act as a 
# relay.

import asyncio
import websockets

hosts = set()
clients = set()

async def handler(websocket):
    role = await websocket.recv()
    if role == "host":
        hosts.add(websocket)
        print("Host connected", flush=True)
    elif role == "client":
        clients.add(websocket)
        print("Client connected", flush=True)
    try:
        async for message in websocket:
            if role == "client":
                # Broadcast keypress to all hosts
                for h in hosts:
                    await h.send(message)
    except:
        pass
    finally:
        if role == "host":
            hosts.remove(websocket)
        elif role == "client":
            clients.remove(websocket)

async def main():
    async with websockets.serve(handler, "0.0.0.0", 8000):
        print("Server running on port 8000...")
        await asyncio.Future()

asyncio.run(main())
