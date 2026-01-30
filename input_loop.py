import asyncio
import os

import api_authentication
import wifi_connection
import mongo_bootstrap


async def status():
    pass
async def scan_ssid():
    await wifi_connection.scan_ssids()
async def select_ssid(ssid_in_use):
    ssid_in_use = asyncio.to_thread(input, "Enter SSID: ")
    print("You have selected: " + ssid_in_use)
async def save_ssid(ssid_in_use):
    valid_ssid = await wifi_connection.password_check(ssid_in_use)
    if valid_ssid:
        pass
    else:
        line = await asyncio.to_thread(input, "Would you like to check the password? (y/n)"
                                              "\nWARNING: THIS WILL TEMPORARILY SHUT OFF "
                                              "YOUR WI-FI FOR 15-20 SECONDS IF YOU PROCEED\n")
        if line == "y":
            line = await asyncio.to_thread(input, "Enter Password: ")
            await wifi_connection.verify_wifi_credentials(ssid_in_use, line)
        else:
            pass
async def scan_devices():
    pass
async def pair_device(db):
    pass
async def connect_to_server(db):
    server_name = os.getenv("SERVER_NAME")
    pairing_ip = await asyncio.to_thread(input, "Enter the IP address of the remote server: ")
    await api_authentication.pair_server(pairing_ip, db)
def test(db):
    print("testing connection")
    db.test_connection()
async def initialize_database(db):
    print("initializing database")
    await mongo_bootstrap.initialize_database(db)
async def drop_database(db):
    decision = await asyncio.to_thread(input, "WARNING: YOU ARE DROPPING COLLECTIONS, "
                                              "DO YOU UNDERSTAND AND WANT TO CONTINUE? (y/n)\n")
    if decision == "y":
        print("dropping collections")
        await mongo_bootstrap.drop_database(db)
    else:
        print("Exiting Drop Database Process")
async def help_info():
    pass

async def shutdown(db):
    db.close()
    print("Server is shutting down")



async def input_loop(db):
    try:
        mydb = db
        ssid_in_use = ""
        input_loop_bool = True
        while input_loop_bool:
            try:
                await asyncio.sleep(1)
                line = await asyncio.to_thread(input, "Enter Command: ")
                line = line.lower()
                match line:
                    case "status":
                        await status()
                    case "scan ssid" | "scan_ssid" | "ssid":
                        await scan_ssid()
                    case "select ssid" | "select_ssid":
                        await select_ssid(ssid_in_use)
                    case "connect to ssid" | "connect" | "connect_to_ssid":
                        await save_ssid(ssid_in_use)
                    case "scan devices" | "scan" | "scan_devices":
                        await scan_devices()
                    case "pair device" | "pair_device":
                        await pair_device(mydb)
                    case "connect to server" | "connect_to_server":
                        await connect_to_server(mydb)
                    case "test":
                        test(mydb)
                    case "initialize database" | "initialize_database":
                        await initialize_database(mydb)
                    case "drop database" | "drop_db":
                        await drop_database(mydb)
                    case "help":
                        await help_info()
                    case "shutdown":
                        await shutdown(mydb)

            except UnicodeDecodeError:
                # This catches the 0xff byte sent by some terminals on Ctrl+C
                break
            except EOFError:
                # This catches Ctrl+D (Unix) or Ctrl+Z (Windows)
                break

    except KeyboardInterrupt:
        # This catches Ctrl+C if it reaches the async loop
        print("\nShutdown signal received.")
    finally:
        print("Cleaning up and exiting...")

