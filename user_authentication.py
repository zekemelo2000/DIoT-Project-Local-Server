import hashlib

import bcrypt
import asyncio
import mongo_connection
from motor.motor_asyncio import AsyncIOMotorClient
from quart import Quart, request, jsonify

async def hash_password(password: str) -> str:
    password_bytes = password.encode('utf-8')
    hashed = await asyncio.to_thread(bcrypt.hashpw,password_bytes, bcrypt.gensalt(rounds=12))
    return hashed.decode('utf-8')

async def verify_password(password: str, hashed_password: str) -> bool:
    password_bytes = password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    return await asyncio.to_thread(bcrypt.checkpw,password_bytes, hashed_bytes)

async def save_user(username: str, password: str, db) -> bool:
    if check_existing_user(username, db):
        print(f"User {username} already exists")
        return False
    hashed_password = await hash_password(password)
    try:
        db.get_collection("local_users").insert_one({"Username": username, "Password": hashed_password})
        return True
    except Exception as e:
        print(f"An error occurred while saving user: {e}")
        return False

async def check_existing_user(user, db):
    collection = db.get_collection("local_users")
    try:
        entry = collection.find_one({"Username": user})
        if entry is not None:
            return True
        else:
            return False
    except Exception as e:
        print(f"An error checking users has occurred: {e}")



