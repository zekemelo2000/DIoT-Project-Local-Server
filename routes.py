import os

from cffi.ffiplatform import maybe_relative_path
from passlib.hash import argon2
from quart import Blueprint, request, jsonify, current_app

import api_authentication

api_bp = Blueprint('api', __name__)

@api_bp.route('/pair-server', methods=['POST','GET'])
async def pair():
    if request.method == "POST":
        db = current_app.mongo_connection
        my_request = await request.get_json()
        admin_token =  request.headers.get("Authorization")
        server_name = my_request.get("server_name")

        if admin_token is None:
            print("admin token was not provided")
            return {"Error no Authorization header"}, 401
        if not api_authentication.check_hash(admin_token):
            print("Error on Server Key")
            return {"error": "Unauthorized"}, 401

        api_key, secret_plaintext, secret_hash = (
            api_authentication.generate_api_credentials())

        secret_hash = argon2.hash(secret_plaintext)
        print(api_key, secret_plaintext, secret_hash)

        await api_authentication.save_key_pair(api_key, secret_hash, db)

        return jsonify({"api_key": api_key,
                        "secret": secret_plaintext}, 200)
    if request.method == "GET":
        return "<h1>Welcome to my Quart GET Server </h1><p>The server is active!</p>"
    return "<h1>Welcome to my Quart Server</h1><p>The server is active!</p>"

@api_bp.route("/")
async def hello():
    return "<h1>Welcome to my Quart Server</h1><p>The server is active!</p>"

# @app.route('/authenticate', methods=['POST'])
# def index():
#     if request.method =='POST':
#         username = request.json.get('API')
#         password = request.json.get('secret')
#     else:
#         return '500'
@api_bp.route('/ESP32', methods=['GET', 'POST'])
async def esp32():
    if request.method == 'POST':
        print('POST was requested.')
        data = request.get_json()

        request_number = data.get('requestNumber')
        print('Request Number: ' + request_number + '\n')

        return '200'
    else:
        return '500'

@api_bp.route('/RemotePair', methods=['GET', 'POST'])
async def remote_pair():
    if request.method == 'POST':
        print('POST was requested.')
        return '200'
    elif request.method == 'GET':
        print('GET was requested.')
        return '200'
    else:
        return '500'