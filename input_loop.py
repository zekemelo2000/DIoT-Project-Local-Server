import asyncio
import os

from bson import ObjectId
import ESP32
import api_authentication
import wifi_connection
import mongo_bootstrap

async def update_env_variable(key, value, file_path=".env"):
    if value is None:
        print(f"Environment variable {key} is not set")
        return

    lines = []
    found = False

    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            for line in f:
                if line.startswith(f"{key}="):
                    lines.append(f"{key}={value}\n")
                    found = True
                else:
                    lines.append(line)

    if not found:
        lines.append(f"{key}={value}\n")

    with open(file_path, "w") as f:
        f.writelines(lines)
        print(f"Environment variable {key} has been updated")

async def status():
    pass
async def scan_ssid():
    await wifi_connection.scan_ssids()
async def select_ssid(ssid_in_use):
    ssid_in_use = asyncio.to_thread(input, "Enter SSID: ")
    print("You have selected: " + ssid_in_use)
async def save_ssid(ssid_in_use):
    if ssid_in_use != os.getenv("WIFI_SSID"):
        print(f"The current SSId in use is not the same as the one saved in .env file")
        line = await asyncio.to_thread(input, "Enter SSID: ")
        await select_ssid(line)
    pw = os.getenv("WIFI_PASSWORD")
    if pw is None:
        print(f"The password is empty")
        line = await asyncio.to_thread(input, "Enter Password: ")
    elif pw == "":
        print(f"The password is empty")
        line = await asyncio.to_thread(input, "Enter Password: ")
    else:
        print(f"The password already exists")
        line = await asyncio.to_thread(input, "Would you like to add a new password? (y/n)\n: ")
        if line == "y":
            line = await asyncio.to_thread(input, "Enter Password: ")
        else:
            return

    if line == "":
        print(f"The password is empty, Exiting process")
        return
    else:
        await update_env_variable("WIFI_SSID", ssid_in_use)
        await update_env_variable("WIFI_PASSWORD", line)
        print(f"Your .env file has been updated with your ssid and password.")
        return

async def scan_devices():
    pass
async def pair_device(db):
    await ESP32.pair_device(db, ObjectId("000000000000000000000001"), "Doggo House", "shielddog24!")

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
        await asyncio.sleep(2)
        mydb = db
        ssid_in_use = ""
        input_loop_bool = True
        while input_loop_bool:
            try:

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
                    case "test update":
                        line = await asyncio.to_thread(input, "Enter Update Value: ")
                        device_dict = {
                          "User__id": {
                            "$oid": "000000000000000000000001"
                          },
                          "Device Name": "Test Device 1",
                          "Device Type": "DUMMY_DEVICE",
                          "Network ID": "esp32-ff453ab4",
                          "API Key": "X6mHyuJree6PKOuIjv9B",
                          "API Secret": "YTxL1xuB0rWQC2nwZyZKCu0V8iJgwfN5"
                        }
                        await ESP32.update_device(device_dict.get("Network ID"),
                                                  device_dict.get("API Key"),device_dict.get("API Secret"), 69)
                        await ESP32.get_data(device_dict.get("Network ID"),
                                             device_dict.get("API Key"), device_dict.get("API Secret"))
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

