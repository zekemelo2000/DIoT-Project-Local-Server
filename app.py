
from pymongo.errors import OperationFailure
import APIAuthentication
import MongoConnection
import asyncio
import WifiConnection
import MongoBootStrap
from quart import Quart, request, jsonify
from dotenv import load_dotenv
from passlib.hash import argon2
import os
app = Quart(__name__)
load_dotenv()

@app.route('/pair-server', methods=['POST','GET'])
async def pair():
    if request.method == "POST":
        admin_token = request.headers.get('Authorization')
        requesting_server_name = request.body.get('server_name')

        if admin_token is None:
            return "Error no Authorization header"
        if not APIAuthentication.check_hash(admin_token, os.getenv("DUMMY_SERVER_KEY")):
            return {"error": "Unauthorized"}, 401

        api_key, secret_plaintext, secret_hash = (
            APIAuthentication.generate_api_credentials())

        secret_hash = argon2.hash(secret_plaintext)

        APIAuthentication.save_key_pair(requesting_server_name, api_key, secret_hash)

        return jsonify({"server_name": os.getenv("SERVER_NAME")
                       ,"api_key": api_key,
                        "secret": secret_plaintext}, 200)
    if request.method == "GET":
        return "<h1>Welcome to my Quart GET Server </h1><p>The server is active!</p>"
    return "<h1>Welcome to my Quart Server</h1><p>The server is active!</p>"

@app.route("/")
async def hello():
    return "<h1>Welcome to my Quart Server</h1><p>The server is active!</p>"

# @app.route('/authenticate', methods=['POST'])
# def index():
#     if request.method =='POST':
#         username = request.json.get('API')
#         password = request.json.get('secret')
#     else:
#         return '500'
@app.route('/ESP32', methods=['GET', 'POST'])
async def esp32():
    if request.method == 'POST':
        print('POST was requested.')
        data = request.get_json()

        request_number = data.get('requestNumber')
        print('Request Number: ' + request_number + '\n')

        return '200'
    else:
        return '500'

@app.route('/RemotePair', methods=['GET', 'POST'])
async def remote_pair():
    if request.method == 'POST':
        print('POST was requested.')
        return '200'
    elif request.method == 'GET':
        print('GET was requested.')
        return '200'
    else:
        return '500'

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

async def server():
    mongoconnection = MongoConnection.get_database("api_keys")
    try:
        print(mongoconnection.find_one({"API key": "test"}))
    except OperationFailure:
        print(f"error has occurred: Authentication required")
    await app.run_task(host="0.0.0.0", port=8080)

async def main():
    await asyncio.gather(server(), input_loop())

if __name__ == '__main__':
    print("Im currently in main")
    asyncio.run(main())





