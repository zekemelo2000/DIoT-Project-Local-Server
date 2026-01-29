import os
from passlib.hash import argon2
from quart import Blueprint
from quart import request, jsonify

import APIAuthentication

api_bp = Blueprint('api', __name__)

@api_bp.route('/pair-server', methods=['POST','GET'])
async def pair():
    if request.method == "POST":
        admin_token = request.headers.get('Authorization')
        requesting_server_name = request.body.get('server_name')

        if admin_token is None:
            return "Error no Authorization header"
        if not APIAuthentication.check_hash(admin_token, os.getenv("DUMMY_SERVER_KEY")):
            return {"error": "Unauthorized"}, 401

        api_key, secret_plaintext, secret_hash = (
            APIAuthentication.generate_api_credentials())

        secret_hash = argon2.hash(secret_plaintext)

        APIAuthentication.save_key_pair(requesting_server_name, api_key, secret_hash)

        return jsonify({"server_name": os.getenv("SERVER_NAME")
                       ,"api_key": api_key,
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