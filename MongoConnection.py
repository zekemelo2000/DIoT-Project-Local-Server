import pymongo
from pymongo import collection, MongoClient
from pymongo.errors import ConnectionFailure

# Replace the placeholder with your actual connection string
CONNECTION_STRING = "mongodb://localhost:27017"
DB_STRING = "local"


def get_database(database_name):
    # Create a connection using MongoClient
    try:
        client = MongoClient(CONNECTION_STRING)
        # The ping command can be used to check if the connection is successful
        client.admin.command('ping')
        #print("MongoDB connection successful!")
        mydb = client[DB_STRING]  # Specify the database to use
        my_collection = mydb[database_name]
        return my_collection


    except ConnectionFailure as e:
        print(f"Could not connect to MongoDB: {e}")
        return None
