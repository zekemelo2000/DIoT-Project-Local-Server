from pymongo.errors import CollectionInvalid

api_keys_validation = {
  "$jsonSchema": {
    "bsonType": "object",
    "required": [
      "Server Name"
      "API key",
      "Hashed secret"
    ],
    "properties": {
      "API key": {
        "bsonType": "string"
      },
      "Hashed secret": {
        "bsonType": "string"
      }
    }
  },
}

api_passport_validation = {
  "$jsonSchema": {
    "bsonType": "object",
    "required": [
      "Server Name"
      "API key",
      "Secret"
    ],
    "properties": {
      "Server Name": {
          "bsonType": "string"
      },
      "API key": {
        "bsonType": "string"
      },
      "Secret": {
        "bsonType": "string"
      }
    }
  },
}

wifi_connections_validation = {
  "$jsonSchema": {
    "bsonType": "object",
    "required": [
      "Password",
      "SSID"
    ],
    "properties": {
      "Password": {
        "bsonType": "string"
      },
      "SSID": {
        "bsonType": "string"
      }
    }
  },
}

local_users_validation = {
  "$jsonSchema": {
    "bsonType": "object",
    "required": [
      "Username",
      "Password"
    ],
    "properties": {
      "Username": {
        "bsonType": "string"
      },
      "Password": {
        "bsonType": "string"
      }
    }
  },
}

remote_users_validation = {
  "$jsonSchema": {
    "bsonType": "object",
    "required": [
      "Username"
      "Password",
      "Local Server"
    ],
    "properties": {
      "Username": {
        "bsonType": "string"
      },
      "Password": {
        "bsonType": "string"
      },
      "Local Server": {
        "bsonType": "string"
      }
    }
  },
}

devices_validation = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": [
            "User__id"
            "Device Name",
            "Device Type",
            "API Key",
            "API Secret"
        ],
        "properties": {
            "User__id": {
                "bsonType": "objectId"
            },
            "Device Name": {
                "bsonType": "string"
            },
            "Device Type": {
                "bsonType": "string"
            },
            "API Key": {
                "bsonType": "string"
            },
            "API Secret": {
                "bsonType": "string"
            }
        }
    },
}

async def initialize_database(db):
    try:
        await db.db.create_collection("api_keys", validator=api_keys_validation )
        print("Collection 'api_keys' created.")
    except CollectionInvalid:
        print("Collection 'api_keys' already exists.")

    try:
        await db.db.create_collection("wifi_connections", validator=wifi_connections_validation )
        print("Collection 'wifi_connections' created.")
    except CollectionInvalid:
        print("Collection 'wifi_connections' already exists.")

    try:
        await db.db.create_collection("api_passport", validator=api_passport_validation )
        print("Collection 'api_passport' created.")
    except CollectionInvalid:
        print("Collection 'api_passport' already exists.")

    try:
        await db.db.create_collection("local_users", validator=local_users_validation)
        print("Collection 'local_users' created.")
    except CollectionInvalid:
        print("Collection 'local_users' already exists.")

    try:
        await db.db.create_collection("remote_users", validator=local_users_validation)
        print("Collection 'remote_users' created.")
    except CollectionInvalid:
        print("Collection 'remote_users' already exists.")

    try:
        await db.db.create_collection("devices", validator=devices_validation)
        print("Collection 'devices' created.")
    except CollectionInvalid:
        print("Collection 'devices' already exists.")

async def drop_database(db):
    collection_name = "api_keys"
    if collection_name in await db.db.list_collection_names():
        await db.db.drop_collection(collection_name)
        print(f"Collection {collection_name} dropped.")
    else:
        print(f"Collection {collection_name} does not exist.")

    collection_name = "wifi_connections"
    if collection_name in await db.db.list_collection_names():
        await db.db.drop_collection(collection_name)
        print(f"Collection {collection_name} dropped.")
    else:
        print(f"Collection {collection_name} does not exist.")

    collection_name = "api_passport"
    if collection_name in await db.db.list_collection_names():
        await db.db.drop_collection(collection_name)
        print(f"Collection {collection_name} dropped.")
    else:
        print(f"Collection {collection_name} does not exist.")

    collection_name = "local_users"
    if collection_name in await db.db.list_collection_names():
        await db.db.drop_collection(collection_name)
        print(f"Collection {collection_name} dropped.")
    else:
        print(f"Collection {collection_name} does not exist.")

    collection_name = "remote_users"
    if collection_name in await db.db.list_collection_names():
        await db.db.drop_collection(collection_name)
        print(f"Collection {collection_name} dropped.")
    else:
        print(f"Collection {collection_name} does not exist.")

    collection_name = "devices"
    if collection_name in await db.db.list_collection_names():
        await db.db.drop_collection(collection_name)
        print(f"Collection {collection_name} dropped.")
    else:
        print(f"Collection {collection_name} does not exist.")