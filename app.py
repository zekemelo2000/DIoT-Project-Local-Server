import asyncio

from dotenv import load_dotenv
from pymongo.errors import OperationFailure
from quart import Quart

import InputLoop
import MongoConnection
from Routes import api_bp

app = Quart(__name__)
app.register_blueprint(api_bp)
load_dotenv()

async def server():
    mongoconnection = MongoConnection.get_database("api_keys")
    try:
        print(mongoconnection.find_one({"API key": "test"}))
    except OperationFailure:
        print(f"error has occurred: Authentication required")
    await app.run_task(host="0.0.0.0", port=8080)

async def main():
    await asyncio.gather(server(), InputLoop.input_loop())

if __name__ == '__main__':
    print("Im currently in main")
    asyncio.run(main())





