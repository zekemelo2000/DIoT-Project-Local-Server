#This file requires user to have a mongodb server and an .env file
#the .env file should include the following parameters:
#MONGO_URI
#MONGO_ADMIN
#MONGO_ADMIN_PASS
#APP_USER
#APP_USER_PASS
#PAYLOAD (This is for making an api key)

import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

admin_user = os.getenv("MONGO_ADMIN_USER")
admin_password = os.getenv("MONGO_ADMIN_PASSWORD")

uri = f"mongodb://{admin_user}:{admin_password}@localhost:27017/?authSource=admin"
client = MongoClient(uri)

