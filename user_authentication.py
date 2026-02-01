import hashlib
from functools import wraps

import bcrypt
import asyncio
import mongo_connection
from motor.motor_asyncio import AsyncIOMotorClient
from quart import Quart, request, jsonify, session


async def hash_password(password: str) -> str:
    """ This function gets called by save_user to save the password hashed """
    password_bytes = password.encode('utf-8')
    hashed = await asyncio.to_thread(bcrypt.hashpw,password_bytes, bcrypt.gensalt(rounds=12))
    return hashed.decode('utf-8')

async def get_devices(user:str, db):
    collection = db.get_collection("local_users")
    entry = await collection.find_one({"Username": user})
    if entry:
        return entry.get('Devices')
    return None

async def get_local_server(user: str, db):
    collection = db.get_collection("remote_users")
    entry = collection.find_one({"Username": user})
    return entry.get('Local Server')

async def verify_local_user(user:str, password: str, db):
    """ This function gets called by @route/local-login to verify user password,
    Function returns """
    serverside = "local_users"
    collection = db.get_collection(serverside)

    entry = await collection.find_one({"Username": user})
    hashed_password = entry['Password']
    if bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8')):
        return True
    else:
        return False

async def register_local_user(user: str, password: str, db):
    """This function gets called by @route/register-login to register user password,
    Function returns a bool """
    serverside = "local_users"
    collection = db.get_collection(serverside)
    hashed_password = await hash_password(password)
    devices = {}
    try:
        message = collection.insert_one({"Username": user, "Password": hashed_password, "Devices": devices})
        return True
    except Exception as e:
        print(f"An error occurred while registering user: {e}")
        return False

async def verify_remote_user(user:str, password: str, db):
    """ This function gets called by @route/remote-login to verify user password,
    Function returns False or the user server information"""
    serverside = "remote_users"
    collection = db.get_collection(serverside)

    hashed_password = hash_password(password)
    entry = collection.find_one_and_update({"Username": user}, {"$set": {"Password": hashed_password}})
    if entry is not None:
        return True
    else:
        return False

#Seems to be the same as register_user
# async def save_user(username: str, password: str, db) -> bool:
#     if check_existing_user(username, db):
#         print(f"User {username} already exists")
#         return False
#     hashed_password = await hash_password(password)
#     try:
#         db.get_collection("local_users").insert_one({"Username": username, "Password": hashed_password})
#         return True
#     except Exception as e:
#         print(f"An error occurred while saving user: {e}")
#         return False

async def check_existing_user(user, db) -> bool:
    collection = db.get_collection("local_users")
    try:
        entry = await collection.find_one({"Username": user})
        if entry is not None:
            #if User already exists
            return True
        else:
            #if User does not exist
            return False
    except Exception as e:
        print(f"An error checking users has occurred: {e}")
        return False




