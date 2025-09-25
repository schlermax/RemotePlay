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

ALLOWED_CLIENTS = {}
IGNORED_CLIENTS = {}

def pick_clients():
    print("Current clients I listen to:\n", ALLOWED_CLIENTS)
    print("Current clients I ignore:\n", IGNORED_CLIENTS)
    print("""
 1. Listen to more clients
 2. Ignore more clients
 3. Done.""")
    pick = input("Type an option: ")

    if pick == '1':
        print(IGNORED_CLIENTS)
        print("Type the client's name to add and press ENTER.")
        print("Type 'done' and press ENTER to exit.")
        person = input('Client name: ')
        while person != 'done':
            if person in IGNORED_CLIENTS:
                IGNORED_CLIENTS.remove(person)
                ALLOWED_CLIENTS.add(person)
                print("Allowed Clients:", ALLOWED_CLIENTS)
                print("Ignored Clients:", IGNORED_CLIENTS)
    elif pick == '2':
        print(ALLOWED_CLIENTS)
        print("Type the client's name to ignore and press ENTER.")
        print("Type 'done' and press ENTER to exit.")
        person = input('Client name: ')
        while person != 'done':
            if person in ALLOWED_CLIENTS:
                ALLOWED_CLIENTS.remove(person)
                IGNORED_CLIENTS.add(person)
                print("Allowed Clients:", ALLOWED_CLIENTS)
                print("Ignored Clients:", IGNORED_CLIENTS)

def pick_keys():
    print("Current keys listened for:\n", ALLOWED_KEYS)
    print("""
 1. Add keys
 2. Remove keys
 3. Done.""")
    pick = input("Type an option: ")

    if pick == '1':
        print("Just start presssing keys to add.")
        print("Press '=' when you are finished.")
        while True:
            key = keyboard.read_event()
            key = key.name
            if key == '=':
                break
            ALLOWED_KEYS.add(key)
            print("Allowed keys:",ALLOWED_KEYS)
    elif pick == '2':
        print("Just start presssing keys to remove.")
        print("Press '=' when you are finished.")
        while True:
            key = keyboard.read_event()
            key = key.name
            if key == '=':
                break
            if key in ALLOWED_KEYS:
                ALLOWED_KEYS.remove(key)
                print("Allowed keys:",ALLOWED_KEYS)




async def host_task():
    name = input("Give yourself a name: ")
    while name == "" or name == 'done':
        print("Not that name.")
        name = input("Give yourself a name: ")
    async with websockets.connect(SERVER_URL) as websocket:
        role_data = {
            'action': 'role_assignment',
            'role': 'host', 
            'name': name
        }
        await websocket.send(json.dumps(role_data))
        print("""You have successfully connected to the relay.
client keystrokes will now be sent to you.
You can block keystrokes by pressing '-'.
This will also pull up a features menu.""")

        async def listen():
            while True:
                raw_msg = await websocket.recv()
                print(raw_msg)
                try:
                    data = json.loads(raw_msg)
                except json.JSONDecodeError:
                    print(f"Received non-JSON message: {raw_msg}", flush=True)
                
                action = data.get("action")
                sender = data.get("sender")

                if sender in ALLOWED_CLIENTS or sender == 'done':
                    if action == "message":
                        print(data["message"])
                    
                    elif action == "all_clients":
                        nms = data["clients"]
                        for nm in nms:
                            ALLOWED_CLIENTS.add(nm)

                    elif action == "new_client":
                        nm = data['client']
                        ALLOWED_CLIENTS.add(nm)
                    
                    elif action == "keystroke":
                        key = data.get("key")
                        press = data.get("press")

                        if key in ALLOWED_KEYS:
                            if press == "down":
                                pyautogui.keyDown(key)
                            elif press == 'up':
                                pyautogui.keyUp(key)
        async def local_input():
            while True:
                keystroke = await asyncio.to_thread(keyboard.read_event)
                if keystroke.name == '-':
                    print("""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
~~~~~~~~~ ~~ ~   FEATURES   MENU   ~ ~~ ~~~~~~~~~
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Welcome to the features menu. Type the number of
the option you want and press ENTER. While this
menu is open, you ignore clients.
                          
 1. Pick which clients I listen to
 2. Pick which keys I listen to
 3. Close menu                        
""")
                    choice = ''
                    while choice != '3':
                        choice = input('Type an option number: ')
                        match choice:
                            case '1':
                                pick_clients()
                            case '2':
                                pick_keys()
                        if choice != '3':
                            print("""
 1. Pick which clients I listen to
 2. Pick which keys I listen to
 3. Close menu
""")
        
        await asyncio.gather(listen(), local_input())

async def client_task():
    name = input("Give yourself a name: ")
    while name == "" or name == 'done':
        print("Not that name.")
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
            keystroke_data = {'action': 'keystroke', 'key':keystroke.name, 'press':keystroke.event_type, 'sender':name}
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
