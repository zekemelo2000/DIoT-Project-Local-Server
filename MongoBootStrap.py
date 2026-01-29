#This file requires user to have a mongodb server and an .env file
#the .env file should include the following parameters:
#MONGO_URI
#APP_USER
#APP_PASS
#PAYLOAD (This is for making an api key)

import os
from urllib.parse import quote_plus
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import OperationFailure, CollectionInvalid

load_dotenv()
user = os.getenv("APP_USER")
password = os.getenv("APP_PASS")
encoded_user = quote_plus(user)
encoded_password = quote_plus(password)

uri = f"mongodb://{encoded_user}:{encoded_password}@localhost:27017/?authSource=admin"

api_keys_validation = {
  "$jsonSchema": {
    "bsonType": "object",
    "required": [
      "Server"
      "API key",
      "Hashed secret"
    ],
    "properties": {
      "Server": {
        "bsonType" : "string"
      },
      "API key": {
        "bsonType": "string"
      },
      "Secret": {
        "bsonType": "string"
      }
    }
  }
}

dummy_api_keys_validation = {
  "$jsonSchema": {
    "bsonType": "object",
    "required": [
      "API key",
      "Secret"
    ],
    "properties": {
      "API key": {
        "bsonType": "string"
      },
      "Secret": {
        "bsonType": "string"
      }
    }
  }
}

wifi_connections_validation = {
  "$jsonSchema": {
    "bsonType": "object",
    "required": [
      "Password",
      "SSID"
    ],
    "properties": {
      "Password": {
        "bsonType": "string"
      },
      "SSID": {
        "bsonType": "string"
      }
    }
  }
}

api_passport_validation = {
  "$jsonSchema": {
    "bsonType": "object",
    "required": [
      "Server"
      "API key",
      "Secret"
    ],
    "properties": {
      "Server": {
          "bsonType" : "string"
      },
      "API key": {
        "bsonType": "string"
      },
      "Secret": {
        "bsonType": "string"
      }
    }
  }
}

def test_connection():
    client = MongoClient(uri)
    try:
        client.admin.command('ping')
        print("Authentication successful.")
    except OperationFailure:
        print("Authentication failed.")
    except Exception as e:
        print(f"An error occurred: {e}")
    client.close()

def initialize_database():
    client = MongoClient(uri)
    db = client["iotdb"]
    try:
        db.create_collection("api_keys", validator=api_keys_validation )
        print("Collection 'api_keys' created.")
    except CollectionInvalid:
        print("Collection 'api_keys' already exists.")

    try:
        db.create_collection("dummy_api_keys", validator=dummy_api_keys_validation )
        print("Collection 'dummy_api_keys' created.")
    except CollectionInvalid:
        print("Collection 'dummy_api_keys' already exists.")

    try:
        db.create_collection("wifi_connections", validator=wifi_connections_validation )
        print("Collection 'wifi_connections' created.")
    except CollectionInvalid:
        print("Collection 'wifi_connections' already exists.")

    try:
        db.create_collection("api_passport_validation", validator=api_passport_validation )
        print("Collection 'api_passport_validation' created.")
    except CollectionInvalid:
        print("Collection 'api_passport_validation' already exists.")

    client.close()

def drop_database():
    client = MongoClient(uri)
    db = client["iotdb"]
    collection_name = "api_keys"
    if collection_name in db.list_collection_names():
        db.drop_collection(collection_name)
        print(f"Collection {collection_name} dropped.")
    else:
        print(f"Collection {collection_name} does not exist.")

    collection_name = "dummy_api_keys"
    if collection_name in db.list_collection_names():
        db.drop_collection(collection_name)
        print(f"Collection {collection_name} dropped.")
    else:
        print(f"Collection {collection_name} does not exist.")

    collection_name = "wifi_connections"
    if collection_name in db.list_collection_names():
        db.drop_collection(collection_name)
        print(f"Collection {collection_name} dropped.")
    else:
        print(f"Collection {collection_name} does not exist.")

    collection_name = "api_passport_validation"
    if collection_name in db.list_collection_names():
        db.drop_collection(collection_name)
        print(f"Collection {collection_name} dropped.")
    else:
        print(f"Collection {collection_name} does not exist.")

    client.close()