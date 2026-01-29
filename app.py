import asyncio

from dotenv import load_dotenv
from pymongo.errors import OperationFailure
from quart import Quart

import input_loop
import mongo_connection
from routes import api_bp

app = Quart(__name__)
mongo_connection = mongo_connection.MongoConnection()
app.mongo_connection = mongo_connection
app.register_blueprint(api_bp)
load_dotenv()

async def server():
    # For connection testing purposes
    mongo_collection = app.mongo_connection.get_collection("api_keys")
    try:
        print(mongo_collection.find_one({"API key": "test"}))
    except OperationFailure:
        print(f"error has occurred: Authentication required")
    await app.run_task(host="0.0.0.0", port=8080)

async def main():
    app.mongo_connection.connect()
    await asyncio.gather(server(), input_loop.InputLoop(app.mongo_connection))

if __name__ == '__main__':
    print("Im currently in main")
    asyncio.run(main())