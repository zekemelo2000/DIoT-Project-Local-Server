import os
import secrets

import requests
from dotenv import load_dotenv
from passlib.hash import argon2
from argon2 import PasswordHasher
import mongo_connection
load_dotenv()

data = os.getenv("PAYLOAD")
API_SECRET = os.getenv("API_SECRET").encode("utf-8")
server_name = os.getenv("SERVER_NAME").encode("utf-8")
server_key = os.getenv("SERVER_KEY").encode("utf-8")
hashed_server_key = os.getenv("HASHED_SERVER_KEY").encode("utf-8")

# Meant to be used by Local Servers to Pair with Remote Servers,
# Could be used by Remote Server to Pair with Local

def check_existing_api_key(api_key,db):
        connection = db.get_collection("api_keys")
        try:
                entry = connection.find_one({"API key": api_key})
                if entry is not None:
                        return True
                else:
                        return False
        except Exception as e:
                print(f"Saving API Key has encountered an error: {e}")

def check_hash(remote_token):
        ph = PasswordHasher()
        try:
                ph.verify(remote_token, hashed_server_key)
                return True
        except Exception as e:
                print(f"Saving API Key has encountered an error: {e}")
                return False

async def save_key_pair(api_key, api_secret, db):
        if check_existing_api_key(api_key, db):
                connection = db.get_collection("api_keys")
                try:
                        connection.insert_one({"API key": api_key, "Hashed secret": api_secret})
                except Exception as e:
                        print(f"Saving API Pair has encountered an error: {e}")

def save_passport_pair(api_key, api_secret, db):
        if check_existing_api_key(api_key, db):
                connection = db.get_collection("api_passport")
                try:
                        connection.insert_one({"API key": api_key, "Secret": api_secret})
                except Exception as e:
                        print(f"Saving Passport Pair has encountered an error: {e}")

def generate_api_credentials():
        # Generate a high-entropy Key and Secret
        api_key = f"pk_{secrets.token_urlsafe(32)}"
        api_secret_plaintext = f"sk_{secrets.token_urlsafe(32)}"

        # Hash the secret before storage
        hashed_secret = argon2.hash(api_secret_plaintext)

        return api_key, api_secret_plaintext, hashed_secret

# Needs to be pushed in with JSON
async def pair_server(pairing_url, db):
        if not pairing_url.startswith(('http://', 'https://')):
                # Default to http://
                pairing_url = f"http://{pairing_url}"
        pairing_url = pairing_url + "/pair-server"

        headers = {"Authorization": server_key}
        body = {"server_name": server_name.decode("utf-8")}

        print(headers)

        response = None
        try:
                response = requests.post(pairing_url.encode('utf-8'), headers=headers, json=body)
        except Exception as e:
                print(f"Saving Pairing has encountered an error: {e}")

        if response.status_code == 200:
                print(response)
                cred = response.json()
                #print(f"Pairing successful.")
                #print(f"API_KEY: {cred[0]["api_key"]}")
                #print(f"API_SECRET: {cred[0]["secret"]}")
                save_passport_pair(cred[0]["api_key"], cred[0]["secret"], db)
        else:
                print(f"Pairing failed.")


# FIX ME to validate later
# def send_connection_request(url, api_key):
#         timestamp = str(int(time.time()))
#
#         #create message with the payload data and time
#         message = f"{timestamp}{data}".encode('utf-8')
#
#         # Generate HMAC signature
#         signature = hmac.new(API_SECRET, message, hashlib.sha256).hexdigest()
#
#         headers = {
#                 "X-API-KEY": api_key,
#                 "X-TIMESTAMP": timestamp,
#                 "X-SIGNATURE": signature,
#                 "Content-Type": "application/json"
#         }
#
#         response = requests.post(url, headers=headers)
#
# REPLAY_WINDOW = 30
#
# async def verify_hmac():
#         api_key = request.headers.get("X-API-KEY")
#         received_signature = request.headers.get("X-SIGNATURE")
#         timestamp = request.headers.get("X-TIMESTAMP")
#
#         if not all([api_key, received_signature, timestamp]):
#                 abort(401, "Missing security headers.")
#
#         current_time = int(time.time())
#         if abs(current_time - int(timestamp)) > REPLAY_WINDOW:
#                 abort(403, "Timestamp out of range.")
#
#         body = await request.get_data()
#         message = f"{timestamp}{body}".encode('utf-8')
#
#         expected_signature = hmac.new(API_SECRET, message, hashlib.sha256).hexdigest()
#
#         if not hmac.compare_digest(received_signature, expected_signature):
#                 abort(403, "Signature verification failed.")
#