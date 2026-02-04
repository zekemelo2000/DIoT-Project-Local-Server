import asyncio
import json
import socket
import string
import time
import httpx
import requests
import my_http
import secrets
from pywifi import PyWiFi, const, Profile
import routes

async def connect_to_esp_wifi():
    wifi = PyWiFi()
    iface = wifi.interfaces()[0]  # Select the first WiFi adapter

    # 1. Create the profile for the ESP32 Recovery AP
    profile = Profile()
    profile.ssid = "ESP32-Pairing-Device"
    profile.auth = const.AUTH_ALG_OPEN
    profile.akm.append(const.AKM_TYPE_WPA2PSK)
    profile.cipher = const.CIPHER_TYPE_CCMP
    profile.key = "password123"  # Must match your WiFi.softAP password

    # 2. Remove existing profiles and connect
    iface.remove_all_network_profiles()
    tmp_profile = iface.add_network_profile(profile)

    print(f"[*] Switching to {profile.ssid}...")
    iface.connect(tmp_profile)

    # 3. Wait for connection (usually takes 5-10 seconds)
    timeout = 15
    start_time = time.time()
    while iface.status() != const.IFACE_CONNECTED:
        time.sleep(1)
        if time.time() - start_time > timeout:
            print("[!] Connection timed out.")
            return False

    print("[*] Connected to ESP32 successfully.")
    return True


def disconnect_wifi():
    wifi = PyWiFi()
    iface = wifi.interfaces()[0]  # Select your WiFi adapter

    print("[*] Disconnecting from ESP32...")
    iface.disconnect()

    # Wait for the interface to actually become disconnected
    timeout = 10
    start_time = time.time()
    while iface.status() != const.IFACE_DISCONNECTED:
        time.sleep(0.5)
        if time.time() - start_time > timeout:
            print("[!] Disconnect timed out.")
            break

    print("[*] WiFi disconnected.")

def generate_random_string(length=16):
    """Generates a secure random alphanumeric string."""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

async def get_my_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip

async def update_device(device_name, device_key, device_secret, update_val):
    """ This is used after login, One device is passed in for you to update"""

    headers = {
        "X-API-Key": device_key,
        "X-API-Secret": device_secret,
    }
    payload = {
        "update_value" : update_val
    }
    response = await my_http.send_request("http://192.168.4.1/update", payload, headers)
    if response.status_code == 200:
        print(f"[*] Successfully updated device: {device_name}")
    else:
        print(f"[*] Failed to update device: {device_name}")


async def get_data(device_api, device_secret):
   payload = {
       "api_key" : device_api,
       "api_secret" : device_secret
   }
   try:
       response = await my_http.send_request("http://192.168.4.1/config", payload)
       try:
           response = response.json()
           value = response.get("value")
           return value
       except Exception as e:
           print(f"[*] The JSON response is malformed: {e}")
           return None
   except Exception as e:
       print(f"[*] The There was an error with the HTTP request: {e}")
       return None


async def pair_device(db, user__id, ssid, pw):
    line = await asyncio.to_thread(input, "WARNING: This will disconnect your WiFi. Continue? (y/n): ")
    if line.lower() != "y": return

    # [CHANGE 2] Check if the server's mDNS is actually running
    if routes.mdns_bus is None:
        print("[!] Error: mDNS system not ready. Wait for the server to fully start.")
        return

    # 1. Connect to ESP32 AP
    await connect_to_esp_wifi()

    # 2. Prepare Config
    new_key = generate_random_string(20)
    new_secret = generate_random_string(32)

    payload = {
        "ssid": ssid,
        "pass": pw,
        "api_key": new_key,
        "api_secret": new_secret
    }

    target_mdns_id = ""
    device_type = ""

    # 3. Send Config
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post("http://192.168.4.1:80/config", json=payload, timeout=10)

        if response.status_code == 200:
            resp_json = response.json()
            device_type = resp_json.get('identity')
            target_mdns_id = resp_json.get('mdns_id')  # Ensure ESP32 sends this!
            print(f"[*] Config sent. Device is: {device_type}")
        else:
            print("[!] ESP32 rejected config.")
            disconnect_wifi()
            return
    except Exception as e:
        print(f"[!] Error talking to ESP32 AP: {e}")
        disconnect_wifi()
        return

    # 4. Reconnect to Home WiFi
    print("[*] Reconnecting to home WiFi...")
    disconnect_wifi()
    # Give it time to switch networks
    await asyncio.sleep(10)

    # 5. Verification
    # If target_mdns_id is None (e.g. old ESP32 code), default to a generic name for testing
    if not target_mdns_id:
        print("[!] Warning: ESP32 didn't return an ID. Using default 'esp32-device-1'")
        target_mdns_id = "esp32-device-1"

    print(f"[*] Searching for {target_mdns_id}.local ...")

    found_ip = None

    # [CHANGE 3] Access mdns_bus via 'routes' module and use the ASYNC method
    service_name = f"{target_mdns_id}._http._tcp.local."

    try:
        # We use async_get_service_info because routes.mdns_bus is an AsyncZeroconf object
        info = await routes.mdns_bus.async_get_service_info("_http._tcp.local.", service_name)

        if info:
            found_ip = socket.inet_ntoa(info.addresses[0])
            print(f"[+] Device verified on network at {found_ip}")
        else:
            print("[!] Warning: Device not found yet (timeout).")
    except Exception as e:
        print(f"[!] mDNS Error: {e}")

    # 6. User Naming
    user_nickname = await asyncio.to_thread(input, "Pairing successful! Enter a name for this device: ")

    query = {
        "User__id": user__id,
        "Device Name": user_nickname,
        "Device Type": device_type,
        "Network ID": target_mdns_id,
        "API Key": new_key,
        "API Secret": new_secret
    }

    db.get_collection("devices").insert_one(query)
    print(f"[*] Saved {user_nickname} to database.")


async def resolve_device_ip(network_id):
    """
    Finds the current IP of a device using its unique Network ID (e.g., 'esp32-4A123F').
    """
    if not network_id:
        print("[!] Error: No Network ID provided.")
        return None

    service_name = f"{network_id}._http._tcp.local."
    print(f"[*] Resolving IP for {network_id}...")

    try:
        # Use the existing mDNS bus from routes
        if routes.mdns_bus is None:
            print("[!] Server mDNS not ready.")
            return None

        info = await routes.mdns_bus.async_get_service_info("_http._tcp.local.", service_name)

        if info:
            ip = socket.inet_ntoa(info.addresses[0])
            print(f"[*] Found {network_id} at {ip}")
            return ip
        else:
            print(f"[!] Device {network_id} not found on network.")
            return None
    except Exception as e:
        print(f"[!] mDNS Error: {e}")
        return None


async def update_device(network_id, api_key, api_secret, new_value):
    # 1. Find IP dynamically
    ip = await resolve_device_ip(network_id)
    if not ip: return

    # 2. Construct Request
    url = f"http://{ip}/update"
    headers = {
        "X-API-Key": api_key,
        "X-API-Secret": api_secret
    }
    payload = {"new_value": str(new_value)}

    # 3. Send
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers, timeout=5)

        if response.status_code == 200:
            print(f"[*] Update Success: {response.text}")
        else:
            print(f"[!] Update Failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"[!] Connection Error: {e}")


async def get_data(network_id, api_key, api_secret):
    # 1. Find IP dynamically
    ip = await resolve_device_ip(network_id)
    if not ip: return

    # 2. Construct Request
    url = f"http://{ip}/get-data"
    headers = {
        "X-API-Key": api_key,
        "X-API-Secret": api_secret
    }
    # Note: Even though it's a "Get Data" request, your C++ uses HTTP_POST for security

    # 3. Send
    try:
        async with httpx.AsyncClient() as client:
            # We send an empty JSON just to trigger the POST handler on ESP32
            response = await client.post(url, json={}, headers=headers, timeout=5)

        if response.status_code == 200:
            data = response.json()
            print("\n--- DEVICE DATA ---")
            print(f"Identity: {data.get('identity')}")
            print(f"Current Value: {data.get('value')}")
            print(f"IP Address: {data.get('ip')}")
            print("-------------------\n")
            return data
        else:
            print(f"[!] Get Data Failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"[!] Connection Error: {e}")
        return None
