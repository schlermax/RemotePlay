# ~~~ USER code ~~~
# This will be executed locally. It will establish a connection with the cloud server relay.
# The user will determine if they are a "host" or "client"

import asyncio
import websockets
import pyautogui

SERVER_URL = "wss://remoteplay.onrender.com"

async def host_task():
    name = input("Give yourself a name: ")
    async with websockets.connect(SERVER_URL) as websocket:
        await websocket.send("host "+name)

        async def listen():
            while True:
                key = await websocket.recv()
                pyautogui.press(key)
        async def local_input():
            while True:
                cmd = input("Enter command (type 'quit' to exit): ")
                if cmd == "quit":
                    break
        
        await asyncio.gather(listen(), local_input())

async def client_task():
    name = input("Give yourself a name: ")
    async with websockets.connect(SERVER_URL) as websocket:
        await websocket.send("client "+name)

        while True:
            key = input("Press key to send: ")
            await websocket.send(key)

async def main():
    print("""Hello, hi. I see you're trying to connect to the server.
If you are hosting, that means the clients will be able press some keys for you.
If you are a client, that means you will be pressing keys for the host.""")
    role = input("Are you a HOST or CLIENT: ").strip().lower()

    while role != "host" and role != "client":
        print(role, "isn't a valid role. Please type 'host' or 'client'.")
        role = input("Are you a host or client? ").strip().lower()

    print("Connecting to relay --", SERVER_URL)

    if role == "host":
        await host_task()
    elif role == "client":
        await client_task()

asyncio.run(main())
