import time
import os
import hashlib
import hmac
import requests
from quart import request, Quart, abort

from cryptography.hazmat.primitives import hmac
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ConnectionFailure, OperationFailure
load_dotenv()

data = os.getenv("PAYLOAD")
API_SECRET = os.getenv("API_SECRET").encode("utf-8")
server_name = os.getenv("SERVER_NAME").encode("utf-8")

# Meant to be used by Local Servers to Pair with Remote Servers,
# Could be used by Remote Server to Pair with Local
def pair_server(pairing_url):
        headers = {"Authorization": f"Bearer {API_SECRET}"}
        body = {"server_name": server_name}

        response = requests.post(pairing_url, headers=headers, json=body)

        if response.status_code == 200:
                cred = response.json()
                print(f"Pairing successful.")
                print(f"API_KEY: {cred['api_key']}")
                print(f"API_SECRET: {cred['api_secret']}")

                # Add to the Database and remove the prints

def send_connection_request(url, api_key):
        timestamp = str(int(time.time()))

        #create message with the payload data and time
        message = f"{timestamp}{data}".encode('utf-8')

        # Generate HMAC signature
        signature = hmac.new(API_SECRET, message, hashlib.sha256).hexdigest()

        headers = {
                "X-API-KEY": api_key,
                "X-TIMESTAMP": timestamp,
                "X-SIGNATURE": signature,
                "Content-Type": "application/json"
        }

        response = requests.post(url, headers=headers)

REPLAY_WINDOW = 30

async def verify_hmac():
        api_key = request.headers.get("X-API-KEY")
        received_signature = request.headers.get("X-SIGNATURE")
        timestamp = request.headers.get("X-TIMESTAMP")

        if not all([api_key, received_signature, timestamp]):
                abort(401, "Missing security headers.")

        current_time = int(time.time())
        if abs(current_time - int(timestamp)) > REPLAY_WINDOW:
                abort(403, "Timestamp out of range.")

        body = await request.get_data()
        message = f"{timestamp}{body}".encode('utf-8')

        expected_signature = hmac.new(API_SECRET, message, hashlib.sha256).hexdigest()

        if not hmac.compare_digest(received_signature, expected_signature):
                abort(403, "Signature verification failed.")

