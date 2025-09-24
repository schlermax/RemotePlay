# ~~~ SERVER code ~~~
# This will not be executed locally. This will be located on the cloud to act as a 
# relay.

import asyncio
import os
import websockets

hosts = {}
clients = {}

# --- Heartbeat Task ---
async def heartbeat():
    while True:
        # Copy the keys so we don’t modify dicts while iterating
        for ws, name in list(hosts.items()):
            try:
                await ws.ping()
            except Exception as e:
                print(f"Heartbeat failed for host ({name}): {e}", flush=True)
                hosts.pop(ws, None)

        for ws, name in list(clients.items()):
            try:
                await ws.ping()
            except Exception as e:
                print(f"Heartbeat failed for client ({name}): {e}", flush=True)
                clients.pop(ws, None)

        await asyncio.sleep(20)  # send ping every 20s

# --- Connection Handler ---
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
        print(f"Host connected ({name})", flush=True)
    elif role == "client":
        clients[websocket] = name
        print(f"Client connected ({name})", flush=True)

    try:
        async for message in websocket:
            if websocket in clients:
                # Broadcast keypress to all hosts
                print(f"Client ({name}) sent: {message}", flush=True)
                for h in list(hosts):
                    try:
                        await h.send(message)
                        print(f"Forwarded to host ({hosts[h]})", flush=True)
                    except Exception as e:
                        print(f"Failed to send to host ({hosts[h]}): {e}", flush=True)
                        hosts.pop(h, None)
    except Exception as e:
        print(f"Error with {role} ({name}): {e}", flush=True)
    finally:
        if role == "host":
            print(f"Host disconnected ({hosts.get(websocket)})", flush=True)
            hosts.pop(websocket, None)
        elif role == "client":
            print(f"Client disconnected ({clients.get(websocket)})", flush=True)
            clients.pop(websocket, None)

# --- Main Entrypoint ---
async def main():
    port = int(os.environ.get("PORT", 8000))
    async with websockets.serve(handler, "0.0.0.0", port, ping_interval=None):
        # Disable built-in pings, use custom heartbeat instead
        print(f"Server running on port {port}...", flush=True)
        await asyncio.gather(
            asyncio.Future(),  # keep running
            heartbeat()
        )

asyncio.run(main())
