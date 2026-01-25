import os
import secrets

import requests
from dotenv import load_dotenv
from passlib.hash import argon2
import MongoConnection

load_dotenv()

data = os.getenv("PAYLOAD")
API_SECRET = os.getenv("API_SECRET").encode("utf-8")
server_name = os.getenv("SERVER_NAME").encode("utf-8")
server_key = os.getenv("SERVER_KEY").encode("utf-8")
# Meant to be used by Local Servers to Pair with Remote Servers,
# Could be used by Remote Server to Pair with Local
def save_key_pair(api_key, api_secret):
        connection = MongoConnection.get_database("api_keys")
        connection.insert_one({"api_key": api_key, "api_secret": api_secret})
        connection.close()

def add_to_passport(api_key, api_secret):
        connection = MongoConnection.get_database("api_passport")
        connection.insert_one({"api_key": api_key, "api_secret": api_secret})
        connection.close()

def generate_api_credentials():
        # 1. Generate a high-entropy Key and Secret
        # 'pk_' for public key, 'sk_' for secret key (common convention)
        api_key = f"pk_{secrets.token_urlsafe(32)}"
        api_secret_plaintext = f"sk_{secrets.token_urlsafe(32)}"

        # 2. Hash the secret before storage
        hashed_secret = argon2.hash(api_secret_plaintext)

        # In a real app, you'd save these to your DB:
        # db.save(key=api_key, secret_hash=hashed_secret)

        return api_key, api_secret_plaintext, hashed_secret

def pair_server(pairing_url):
        headers = {"Authorization": server_key}
        body = {"server_name": server_name}

        response = requests.post(pairing_url, headers=headers, json=body)

        if response.status_code == 200:
                cred = response.json()
                print(f"Pairing successful.")
                print(f"API_KEY: {cred['api_key']}")
                print(f"API_SECRET: {cred['api_secret']}")

                # FIX MEAdd to the Database and remove the prints

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
