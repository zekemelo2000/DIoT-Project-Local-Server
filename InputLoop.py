import asyncio
import os

from dotenv import load_dotenv
from quart import Quart

import APIAuthentication
import MongoBootStrap
import WifiConnection
from Routes import api_bp

app = Quart(__name__)
app.register_blueprint(api_bp)
load_dotenv()

async def input_loop():
    ssid_in_use = ""
    input_loop_bool = True
    while input_loop_bool:
        await asyncio.sleep(1)
        line = await asyncio.to_thread(input, "Enter Command: ")
        line = line.lower()
        match line:
            case "status":
                pass
            case "scan ssid" | "scan_ssid" | "ssid":
                await WifiConnection.scan_ssids()
            case "select ssid" | "select_ssid":
                ssid_in_use = await asyncio.to_thread(input, "Enter SSID: ")
                print("You have selected: " + ssid_in_use)
            case "connect to ssid" | "connect" | "connect_to_ssid":
                valid_ssid = await WifiConnection.password_check(ssid_in_use)
                if valid_ssid:
                    pass
                else:
                    line = await asyncio.to_thread(input, "Would you like to check the password? (y/n)"
                    "\nWARNING: THIS WILL TEMPORARILY SHUT OFF YOUR WI-FI FOR 15-20 SECONDS IF YOU PROCEED\n")
                    if line == "y":
                        line = await asyncio.to_thread(input, "Enter Password: ")
                        await WifiConnection.verify_wifi_credentials(ssid_in_use, line)
                    else:
                        pass
            case "scan devices" | "scan" | "scan_devices":
                pass
            case "connect device" | "connect_to_device":
                pass
            case "connect to remote server" | "connect_to_remote_server":
                server_name = os.getenv("SERVER_NAME")
                pairing_ip = await asyncio.to_thread(input, "Enter the IP address of the remote server: ")
                APIAuthentication.pair_server(pairing_ip)
            case "show log" | "show_log":
                pass
            case "shutdown":
                pass
            case "reset":
                pass
            case "factory reset" | "factory_reset":
                pass
            case "test":
                print("testing connection")
                MongoBootStrap.test_connection()
            case "initialize database" | "initialize_database":
                print("initializing database")
                MongoBootStrap.initialize_database()
            case "drop database" | "drop_db":
                decision = await asyncio.to_thread(input, "WARNING: YOU ARE DROPPING COLLECTIONS, "
                                                          "DO YOU UNDERSTAND AND WANT TO CONTINUE? (y/n)\n")
                if decision == "y":
                    print("dropping collections")
                    MongoBootStrap.drop_database()
                else:
                    print("Exiting Drop Database Process")
            case "help":
                pass