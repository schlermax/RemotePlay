# ~~~ SERVER code ~~~
# Cloud relay server

import asyncio
import os
import websockets
import json

hosts = {}
clients = {}

# --- Heartbeat Task ---
async def heartbeat():
    while True:
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
    role = None
    name = None

    try:
        async for raw_msg in websocket:
            try:
                data = json.loads(raw_msg)
            except json.JSONDecodeError:
                print(f"Received non-JSON message: {raw_msg}", flush=True)
                continue

            action = data.get("action")

            print(f"PACKET: {data}", flush=True)

            # --- Handle role assignment ---
            if action == "role_assignment":
                role = data.get("role")
                name = data.get("name")

                if role == "host":
                    hosts[websocket] = name
                    print(f"Host connected ({name})", flush=True)
                    for h in list(hosts):
                        try:
                            nms = []
                            for c in clients:
                                nms.append(clients[c])
                            data = {'action': 'all_clients', 'clients': nms, 'sender':'done'}
                            await h.send(json.dumps(data))  # forward JSON to hosts
                            print(f"Forwarded to host ({hosts[h]})", flush=True)
                        except Exception as e:
                            print(f"Failed to send to host ({hosts[h]}): {e}", flush=True)
                            hosts.pop(h, None)
                
                elif role == "client":
                    clients[websocket] = name
                    print(f"Client connected ({name})", flush=True)
                    for h in list(hosts):
                        try:
                            data = {'action': 'new_client', 'client': name, 'sender':'done'}
                            await h.send(json.dumps(data))  # forward JSON to hosts
                            print(f"Forwarded to host ({hosts[h]})", flush=True)
                        except Exception as e:
                            print(f"Failed to send to host ({hosts[h]}): {e}", flush=True)
                            hosts.pop(h, None)
                else:
                    print(f"Invalid role: {role}", flush=True)
                
                print(f"Hosts: {hosts}", flush=True)
                print(f"Clients: {clients}", flush=True)

            # --- Handle client messages ---
            elif action == "message" and websocket in clients:
                print(f"Client ({clients[websocket]}) sent: {data}", flush=True)
                for h in list(hosts):
                    try:
                        await h.send(raw_msg)  # forward JSON to hosts
                        print(f"Forwarded to host ({hosts[h]})", flush=True)
                    except Exception as e:
                        print(f"Failed to send to host ({hosts[h]}): {e}", flush=True)
                        hosts.pop(h, None)
            
            # --- Handle client key strokes ---
            elif action == "keystroke" and websocket in clients:
                print(f"Client ({clients[websocket]}) sent: {data}", flush=True)
                for h in list(hosts):
                    try:
                        await h.send(raw_msg)  # forward JSON to hosts
                        print(f"Forwarded to host ({hosts[h]})", flush=True)
                    except Exception as e:
                        print(f"Failed to send to host ({hosts[h]}): {e}", flush=True)
                        hosts.pop(h, None)

    except Exception as e:
        print(f"Error with {role or 'unknown'} ({name or 'unknown'}): {e}", flush=True)

    finally:
        if websocket in hosts:
            print(f"Host disconnected ({hosts.get(websocket)})", flush=True)
            hosts.pop(websocket, None)
        elif websocket in clients:
            print(f"Client disconnected ({clients.get(websocket)})", flush=True)
            clients.pop(websocket, None)


# --- Main Entrypoint ---
async def main():
    port = int(os.environ.get("PORT", 8000))
    async with websockets.serve(handler, "0.0.0.0", port, ping_interval=None):
        print(f"Server running on port {port}...", flush=True)
        await asyncio.gather(
            asyncio.Future(),  # keep running
            heartbeat()
        )

asyncio.run(main())
