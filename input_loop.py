import asyncio
import os

from dotenv import load_dotenv
from quart import Quart

import api_authentication
import mongo_bootstrap
import wifi_connection
from routes import api_bp

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
                        pass
                    case "scan ssid" | "scan_ssid" | "ssid":
                        await wifi_connection.scan_ssids()
                    case "select ssid" | "select_ssid":
                        ssid_in_use = await asyncio.to_thread(input, "Enter SSID: ")
                        print("You have selected: " + ssid_in_use)
                    case "connect to ssid" | "connect" | "connect_to_ssid":
                        valid_ssid = await wifi_connection.password_check(ssid_in_use)
                        if valid_ssid:
                            pass
                        else:
                            line = await asyncio.to_thread(input, "Would you like to check the password? (y/n)"
                                                                  "\nWARNING: THIS WILL TEMPORARILY SHUT OFF YOUR WI-FI FOR 15-20 SECONDS IF YOU PROCEED\n")
                            if line == "y":
                                line = await asyncio.to_thread(input, "Enter Password: ")
                                await wifi_connection.verify_wifi_credentials(ssid_in_use, line)
                            else:
                                pass
                    case "scan devices" | "scan" | "scan_devices":
                        pass
                    case "connect device" | "connect_to_device":
                        pass
                    case "connect to remote server" | "connect_to_remote_server":
                        server_name = os.getenv("SERVER_NAME")
                        pairing_ip = await asyncio.to_thread(input, "Enter the IP address of the remote server: ")
                        api_authentication.pair_server(pairing_ip)
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
                        db.test_connection()
                    case "initialize database" | "initialize_database":
                        print("initializing database")
                        mongo_bootstrap.initialize_database(mydb)
                    case "drop database" | "drop_db":
                        decision = await asyncio.to_thread(input, "WARNING: YOU ARE DROPPING COLLECTIONS, "
                                                                  "DO YOU UNDERSTAND AND WANT TO CONTINUE? (y/n)\n")
                        if decision == "y":
                            print("dropping collections")
                            mongo_bootstrap.drop_database(mydb)
                        else:
                            print("Exiting Drop Database Process")
                    case "help":
                        pass

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

