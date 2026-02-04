import time
import pywifi
from pywifi import const
import asyncio
import mongo_connection
import collections.abc

async def scan_ssids():
    wifi = pywifi.PyWiFi()
    iface =wifi.interfaces()[0]

    iface.scan()
    print("Scanning for SSIDs...")
    await asyncio.sleep(2)

    results = iface.scan_results()
    print(f"{'SSID':<25} | {'Signal Power'}")
    for network in results:
        print(f"{network.ssid:<25} | {network.signal}")

async def verify_wifi_credentials(ssid, password):
    """Bridge function to run the blocking Wi-Fi logic in a background thread."""
    return await asyncio.to_thread(sync_verify_wifi, ssid, password)


def sync_verify_wifi(ssid, password):
    wifi = pywifi.PyWiFi()
    iface = wifi.interfaces()[0]  # Get the primary Wi-Fi card

    # 1. Capture the original network name
    original_ssid = None
    if iface.status() == const.IFACE_CONNECTED:
        # We look at the currently active profile
        current_profiles = iface.network_profiles()
        if current_profiles:
            # Most interfaces keep the 'active' profile at index 0
            original_ssid = current_profiles[0].ssid
            print(f"Current network detected: {original_ssid}")

    # 2. Setup the Test Profile
    iface.disconnect()
    time.sleep(1.5)  # Wait for hardware to release the connection

    profile = pywifi.Profile()
    profile.ssid = ssid
    profile.key = password
    profile.auth = const.AUTH_ALG_OPEN
    profile.akm.append(const.AKM_TYPE_WPA2PSK)  # Standard WPA2
    profile.cipher = const.CIPHER_TYPE_CCMP

    # SAFER STEP: Don't remove all. Just add this one.
    # We remove any previous profile with the SAME name to avoid conflicts.
    all_existing = iface.network_profiles()
    for p in all_existing:
        if p.ssid == ssid:
            iface.remove_network_profile(p)

    test_profile = iface.add_network_profile(profile)
    iface.connect(test_profile)

    # 3. Monitor Connection Status
    print(f"Testing password for {ssid}...")
    success = False
    for i in range(12):  # Give it ~12 seconds
        status = iface.status()
        print(f"Current Status: {status}")
        if iface.status() == 3:
            success = True
            print(f"Test Successful. Attempting to reconnect to original: {original_ssid}")
            line = input("Would you like to save the ssid and password? (y/n) ")
            if line.lower() == "y":

                mongoconnection = MongoConnection.get_database("wifi_connections")
                result = mongoconnection.insert_one({"SSID": ssid, "Password": password})
                if result.acknowledged:
                    print("The SSID and Password has been saved.")
                else:
                    print("The SSID and Password has been NOT saved.")
            break
        time.sleep(1)

    # 4. SAFER CLEAN UP: Restore original connection
    if not success:
        print(f"Test failed for {ssid}.")
        if original_ssid:
            print(f"Attempting to restore connection to {original_ssid}...")
            # We remove the failed test profile so it doesn't stay in system
            iface.remove_network_profile(test_profile)

            # Find and reconnect to the original
            all_profiles = iface.network_profiles()
            for p in all_profiles:
                if p.ssid == original_ssid:
                    iface.connect(p)
                    break
    else:
        print(f"Successfully connected to {ssid}!")

    return success