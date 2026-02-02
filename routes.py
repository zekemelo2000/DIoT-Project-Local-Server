import os

from cffi.ffiplatform import maybe_relative_path
from passlib.hash import argon2
from quart import Blueprint, request, jsonify, current_app, session, redirect, render_template, url_for
from functools import wraps


import api_authentication
import user_authentication

api_bp = Blueprint('api', __name__)

def login_required(f):
    @wraps(f)
    async def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({"message": "You must be logged in to access this page"}), 401

        session.modified = True
        return await f(*args, **kwargs)

    return decorated_function

@api_bp.route('/check-session', methods =['GET'])
async def check_session():
    if 'user_id' in session:
        return jsonify({
            "authenticated": True,
            "user": session["user_id"],
            "devices": session.get('login_devices', [])
        }), 200
    return jsonify({"authenticated": False}), 401

@api_bp.route('/local-register', methods=['POST'])
async def local_register():
    if request.method == 'POST':
        my_request = None
    if request.is_json:
        my_request = await request.get_json()
    elif request.form:
        my_form = await request.form
        my_request = my_form.to_dict()
    else:
        return "Unknown format", 400

    username = my_request.get("username")
    password = my_request.get("password")
    db = current_app.mongo_connection

    if await user_authentication.check_existing_user(username, db):
        return "User already exists", 401

    if not await user_authentication.register_local_user(username, password, db):
        return "There was an error registering the user", 500

    return jsonify({"message": "User registered"}), 200

@api_bp.route('/local-login', methods=['POST'])
async def local_login():
    if request.method == 'POST':
        my_request = None
        if request.is_json:
            my_request = await request.get_json()
        elif request.form:
            my_form = await request.form
            my_request = my_form.to_dict()
        else:
            return "Unknown format", 400

        username = my_request.get("username")
        password = my_request.get("password")
        user__id = my_request.get("user__id")
        db = current_app.mongo_connection

        login_devices = await user_authentication.verify_local_user(username, password,db)
        if not login_devices:
            return jsonify({"message": "Invalid Credentials"}), 401

        #do something with devices

        session.permanent = True
        session['user_id'] = str(user__id)
        session['login_devices'] = await user_authentication.get_devices(user__id, db)
        return  jsonify({
            "status": "success",
            "redirect_url": "/devices",
            "message": "Logged in successfully"
        }),200
    return print("this is the default route")


@api_bp.route('/remote-login', methods=['POST'])
async def remote_login():
    if request.method == 'POST':
        my_request = None
        if request.is_json:
            my_request = await request.get_json()
        elif request.form:
            my_form = await request.form
            my_rq = my_form.to_dict()
        else:
            return "Unknown format", 400

        username = my_request.get("user_name")
        password = my_request.get("password")

        # Verify user credentials
        db = current_app.mongo_connection

        user = user_authentication.verify_remote_user(username, password,db)
        if not user:
            return jsonify({"message": "Invalid Credentials"}), 401


        session.permanent = True
        session['user_id'] = username
        return jsonify({f"User: {username} has validated their session"}),200
    return None

@api_bp.route('/logout')
async def logout():
    session.clear()
    return jsonify({"message": "Logged out."})

@api_bp.route('/devices', methods=["GET"])
@login_required
async def devices():
    if request.method == 'GET':
        return "This is the device GET page"
    else:
        return "This is the device page"


@api_bp.route('/pass-remote-to-local', methods=['GET', 'POST'])
@login_required
async def passRemoteToLocal():
    if request.method == 'POST':

        #Need to reauthorize user to get the OK
        #Once OK signal is established allow the use of ESP32 devices
        #Need to figure out how it looks like to have an "OK" to use ESP32 devices
        pass
    elif request.method == 'GET':
        pass



@api_bp.route('/pair-server', methods=['POST','GET'])
async def pair():
    if request.method == "POST":
        db = current_app.mongo_connection
        my_request = await request.get_json()
        admin_token =  request.headers.get("Authorization")
        server_name = my_request.get("server_name")

        if api_authentication.check_existing_server(server_name,db):
            print("Server already exists, No further action will be taken.")
            return 400
        if admin_token is None:
            print("admin token was not provided")
            return {"Error no Authorization header"}, 400
        if not api_authentication.check_hash(admin_token):
            print("Error on Server Key")
            return {"error": "Unauthorized"}, 401

        api_key, secret_plaintext, secret_hash = (
            api_authentication.generate_api_credentials())

        secret_hash = argon2.hash(secret_plaintext)

        await api_authentication.save_key_pair(server_name, api_key, secret_hash, db)

        own_server_name = os.getenv("SERVER_NAME")
        return jsonify({"server_name": own_server_name,
                        "api_key": api_key,
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