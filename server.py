# ~~~ SERVER code ~~~
# This will not be executed locally. This will be located on the cloud to act as a 
# relay.

import asyncio
import os
import websockets

hosts = {}
clients = {}

async def handler(websocket):
    role_and_name = await websocket.recv()
    role_and_name = role_and_name.split()

    if len(role_and_name) != 2:
        print("Invalid role/name received", flush=True)
        return
    
    role = role_and_name[0]
    name = role_and_name[1]

    if role == "host":
        hosts[websocket] = name
        print(f"Host connected ({hosts.get(websocket)})", flush=True)
    elif role == "client":
        clients[websocket] = name
        print(f"Client connected ({clients.get(websocket)})", flush=True)
    try:
        async for message in websocket:
            if role == "client":
                # Broadcast keypress to all hosts
                print("Client sent message: "+message, flush=True)
                for h in hosts:
                    await h.send(message)
    except:
        pass
    finally:
        if role == "host":
            print(f"Host disconnected ({hosts.get(websocket)})", flush=True)
            hosts.pop(websocket, None)
        elif role == "client":
            print(f"Client disconnected ({hosts.get(websocket)})", flush=True)
            hosts.pop(websocket, None)

async def main():
    port = int(os.environ.get("PORT", 8000))
    async with websockets.serve(handler, "0.0.0.0", port):
        print("Server running on port 8000...")
        await asyncio.Future()

asyncio.run(main())
