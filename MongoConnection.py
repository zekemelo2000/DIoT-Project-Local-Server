from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

class MongoConnection:
    def __init__(self):
        self.client = None
        self.connection_string = "mongodb://localhost:27017"
        self.db_name = "iotdb"
        #self.client = MongoClient(self.connection_string)
        #self.db = self.client[self.db_name]

    def connect(self):
        try:
            self.client = MongoClient(self.connection_string)
            print(f"connected to db: {self.db_name}")
        except ConnectionFailure:
            print("Could not connect to specific database")

    def close(self):
        self.client.close()

    def get_database(self, database_name):
        # Create a connection using MongoClient
        try:
            client = MongoClient(self.connection_string)
            # The ping command can be used to check if the connection is successful
            client.admin.command('ping')
            # print("MongoDB connection successful!")
            mydb = client[self.db_name]  # Specify the database to use
            my_collection = mydb[database_name]
            return my_collection


        except ConnectionFailure as e:
            print(f"Could not connect to MongoDB: {e}")
            return None

# pass the collection name
# when using make sure to add close()
