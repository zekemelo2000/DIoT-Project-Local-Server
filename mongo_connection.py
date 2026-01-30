import os
from urllib.parse import quote_plus

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure
from motor.motor_asyncio import AsyncIOMotorClient


class MongoConnection:
    def __init__(self):
        load_dotenv()
        self.encoded_user = quote_plus(os.getenv("APP_USER"))
        self.encoded_password = quote_plus(os.getenv("APP_PASS"))
        self.client = None
        self.connection_string = f"mongodb://{self.encoded_user}:{self.encoded_password}@localhost:27017/?authSource=admin"
        self.db_name = "iotdb"
        #self.client = MongoClient(self.connection_string)
        self.db = None

    def connect(self):
        try:
            self.client = AsyncIOMotorClient(self.connection_string)
            self.db = self.client[self.db_name]
            print(f"connected to db: {self.db_name}")
        except ConnectionFailure:
            print("Could not connect to specific database")

    def get_collection(self, database_name):
        # Create a collection using MongoClient
        try:
            my_collection = self.db[database_name]
            return my_collection

        except ConnectionFailure as e:
            print(f"Could not connect to MongoDB: {e}")
            return None

    def test_connection(self):
        try:
            self.client.admin.command('ping')
            print("Authentication successful.")
        except OperationFailure:
            print("Authentication failed.")
        except Exception as e:
            print(f"An error occurred: {e}")

    def close(self):
        self.client.close()