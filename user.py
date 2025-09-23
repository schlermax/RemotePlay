# ~~~ USER code ~~~
# This will be executed locally. It will establish a connection with the cloud server relay.
# The user will determine if they are a "host" or "client"

import asyncio
import websockets
import pyautogui

SERVER_URL = "wss://your-render-service.onrender.com"

async def host_task():
    async with websockets.connect(SERVER_URL) as websocket:
        await websocket.send("host")

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
    async with websockets.connect(SERVER_URL) as websocket:
        await websocket.send("client")
        while True:
            key = input("Press key to send: ")
            await websocket.send(key)

async def main():
    role = input("Are you a host or client? ").strip().lower()

    if role == "host":
        await host_task()
    elif role == "client":
        await client_task()
    else:
        print("Invalid role. Please restart and type 'host' or 'client'.")

asyncio.run(main())
