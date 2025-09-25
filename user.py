# ~~~ USER code ~~~
# This will be executed locally. It will establish a connection with the cloud server relay.
# The user will determine if they are a "host" or "client"

import asyncio
import json
import keyboard
import pyautogui
import websockets

SERVER_URL = "wss://remoteplay.onrender.com"

ALLOWED_KEYS = {'up', 'down', 'left', 'right', 'z', 'x', 'c'}

async def host_task():
    name = input("Give yourself a name: ")
    async with websockets.connect(SERVER_URL) as websocket:
        role_data = {
            'action': 'role_assignment',
            'role': 'host', 
            'name': name
        }
        await websocket.send(json.dumps(role_data))

        async def listen():
            while True:
                raw_msg = await websocket.recv()
                print(raw_msg)
                try:
                    data = json.loads(raw_msg)
                except json.JSONDecodeError:
                    print(f"Received non-JSON message: {raw_msg}", flush=True)
                
                action = data.get("action")
                if action == "message":
                    print(data["message"])
                elif action == "keystroke":
                    key_event = data.get("key")
                    key = key_event.name
                    press = key_event.event_type

                    if key in ALLOWED_KEYS:
                        if press == "down":
                            pyautogui.keyDown(key)
                        elif press == 'up':
                            pyautogui.keyUp(key)
        async def local_input():
            while True:
                cmd = input("Enter command (type 'quit' to exit): ")
                if cmd == "quit":
                    break
        
        await asyncio.gather(listen(), local_input())

async def client_task():
    name = input("Give yourself a name: ")
    async with websockets.connect(SERVER_URL) as websocket:
        role_data = {
            'action': 'role_assignment',
            'role': 'client', 
            'name': name
        }
        await websocket.send(json.dumps(role_data))
        print("""You have successfully connected to the relay.
Your keystrokes will now be sent to the host(s).
You can mute your keystrokes by pressing '-'.""")

        while True:
            # key = await asyncio.to_thread(input, "Press key to send: ")
            # msg_data = {'action': 'message', 'message': key}
            # await websocket.send(json.dumps(msg_data))
            paused = False
            keystroke = await asyncio.to_thread(keyboard.read_event)
            keystroke_data = {'action': 'keystroke', 'key':keystroke}
            if keystroke.name == '-':
                paused = True
                print("You have muted your keystrokes. Press '=' to unmute.")
            elif keystroke.name == '=':
                paused = False
                print("You have unmuted your keystrokes. Press '-' to mute.")
            elif not paused:
                await websocket.send(json.dumps(keystroke_data))

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
