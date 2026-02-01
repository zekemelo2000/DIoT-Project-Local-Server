import asyncio

from dotenv import load_dotenv
from pymongo.errors import OperationFailure
from quart import Quart
import redis
from redis import asyncio as aioredis
import input_loop
import mongo_connection
from routes import api_bp
from datetime import timedelta
from quart_session import Session

#load environment first
load_dotenv()

#initialize the app
app = Quart(__name__)

#configure redis
app.config["SESSION_TYPE"] = 'redis'
app.config['SESSION_REDIS'] = aioredis.from_url('redis://localhost:6379')
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=5)

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