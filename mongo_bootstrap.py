from pymongo.errors import CollectionInvalid

api_keys_validation = {
  "$jsonSchema": {
    "bsonType": "object",
    "required": [
      "Server"
      "API key",
      "Hashed secret"
    ],
    "properties": {
      "Server": {
        "bsonType" : "string"
      },
      "API key": {
        "bsonType": "string"
      },
      "Secret": {
        "bsonType": "string"
      }
    }
  },
  "validationLevel": "strict",
  "validationAction": "error"
}

dummy_api_keys_validation = {
  "$jsonSchema": {
    "bsonType": "object",
    "required": [
      "API key",
      "Secret"
    ],
    "properties": {
      "API key": {
        "bsonType": "string"
      },
      "Secret": {
        "bsonType": "string"
      }
    }
  },
  "validationLevel": "strict",
  "validationAction": "error"
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
  "validationLevel": "strict",
  "validationAction": "error"
}

api_passport_validation = {
  "$jsonSchema": {
    "bsonType": "object",
    "required": [
      "Server"
      "API key",
      "Secret"
    ],
    "properties": {
      "Server": {
          "bsonType" : "string"
      },
      "API key": {
        "bsonType": "string"
      },
      "Secret": {
        "bsonType": "string"
      }
    }
  },
  "validationLevel": "strict",
  "validationAction": "error"
}


def initialize_database(db):
    try:
        db.create_collection("api_keys", validator=api_keys_validation )
        print("Collection 'api_keys' created.")
    except CollectionInvalid:
        print("Collection 'api_keys' already exists.")

    try:
        db.create_collection("dummy_api_keys", validator=dummy_api_keys_validation )
        print("Collection 'dummy_api_keys' created.")
    except CollectionInvalid:
        print("Collection 'dummy_api_keys' already exists.")

    try:
        db.create_collection("wifi_connections", validator=wifi_connections_validation )
        print("Collection 'wifi_connections' created.")
    except CollectionInvalid:
        print("Collection 'wifi_connections' already exists.")

    try:
        db.create_collection("api_passport_validation", validator=api_passport_validation )
        print("Collection 'api_passport_validation' created.")
    except CollectionInvalid:
        print("Collection 'api_passport_validation' already exists.")

def drop_database(db):
    collection_name = "api_keys"
    if collection_name in db.list_collection_names():
        db.drop_collection(collection_name)
        print(f"Collection {collection_name} dropped.")
    else:
        print(f"Collection {collection_name} does not exist.")

    collection_name = "dummy_api_keys"
    if collection_name in db.list_collection_names():
        db.drop_collection(collection_name)
        print(f"Collection {collection_name} dropped.")
    else:
        print(f"Collection {collection_name} does not exist.")

    collection_name = "wifi_connections"
    if collection_name in db.list_collection_names():
        db.drop_collection(collection_name)
        print(f"Collection {collection_name} dropped.")
    else:
        print(f"Collection {collection_name} does not exist.")

    collection_name = "api_passport_validation"
    if collection_name in db.list_collection_names():
        db.drop_collection(collection_name)
        print(f"Collection {collection_name} dropped.")
    else:
        print(f"Collection {collection_name} does not exist.")
