import asyncio
import os

from dotenv import load_dotenv
from pymongo.errors import OperationFailure
from quart import Quart
from redis import asyncio as aioredis
import input_loop
import mongo_connection
from routes import api_bp
from datetime import timedelta
from quart_session import Session
from quart_cors import cors

#load environment first
load_dotenv()

localip = os.getenv("LOCALIP")
#initialize the app
app = Quart(__name__)
app = cors(
    app,
    allow_origin=f"http://{localip}:3000",
    allow_credentials=True
)

#configure redis
api_secret_key = os.getenv("API_SECRET_KEY")
app.secret_key = api_secret_key
app.config["SESSION_TYPE"] = 'redis'
app.config['SESSION_REDIS'] = aioredis.from_url('redis://localhost:6379')
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=5)
app.config['SERVER_SETTINGS'] = {

}
app.config.update(
    SESSION_COOKIE_SAMESITE='Lax',  # Allows cookies to be sent across your proxy
    SESSION_COOKIE_HTTPONLY=True,   # Prevents JavaScript from accessing the cookie
    SESSION_COOKIE_SECURE=False,    # Set to True only if you are using HTTPS/SSL
)

#hook session in
Session(app)

#initialize database connection
app.mongo_connection = mongo_connection.MongoConnection()

#register blueprint
app.register_blueprint(api_bp)

async def server():
    # For connection testing purposes
    mongo_collection = app.mongo_connection.get_collection("api_keys")
    try:
        entry = await mongo_collection.find_one({"API key": "test"})
        if entry is not None:
            print(f"API key is {entry['API key']}")
            print(f"Dummy secret is {entry['Hashed secret']}")
    except OperationFailure:
        print(f"error has occurred: Authentication required")
    finally:
        await app.run_task(host="0.0.0.0", port=8080)

async def main():
    app.mongo_connection.connect()
    await asyncio.gather(server(), input_loop.input_loop(app.mongo_connection))
    return 0

if __name__ == '__main__':
    print("Im currently in main")
    asyncio.run(main())