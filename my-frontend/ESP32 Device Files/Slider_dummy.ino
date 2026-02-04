#include <WiFi.h>
#include <WebServer.h>
#include <Preferences.h>
#include <ArduinoJson.h>
#include <HTTPClient.h>
#include <ESPmDNS.h>

const String DEVICE_TYPE = "slider_device";

Preferences prefs;
WebServer server(80);

String ssid, pass, api_key, api_secret, value, server_ip;
unsigned long lastPingTime = 0;
const unsigned long PING_INTERVAL = 30000; // 5 minutes
bool isRecoveryMode = false;

void startRecoveryAP() {
  // We don't check 'isRecoveryMode' here because we want to be able 
  // to force-restart it after a failed heartbeat check.
  Serial.println("Action: Enabling Recovery AP...");
  WiFi.mode(WIFI_AP_STA); 
  WiFi.softAP("ESP32-Pairing-Device", "password123");
  isRecoveryMode = true;
}

void checkHeartbeat() {
  // 1. Recovery Mode Logic (unchanged)
  if (isRecoveryMode) {
    Serial.println("Heartbeat: Checking if Home WiFi/Server is back...");
    WiFi.begin(ssid.c_str(), pass.c_str());
    int attempt = 0;
    while (WiFi.status() != WL_CONNECTED && attempt < 20) {
      delay(500); Serial.print("."); attempt++;
    }
  }

  // 2. Only proceed if connected
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\nBrowsing for mDNS service...");
    
    // queryService returns the number of services found
    int n = MDNS.queryService("http", "tcp"); 

    if (n == 0) {
      Serial.println("No mDNS services found at all.");
    } else {
      Serial.print(n); Serial.println(" service(s) found!");
      
      for (int i = 0; i < n; ++i) {
        // --- DEBUGGING PRINTS ---
        Serial.print("  ["); Serial.print(i); Serial.print("] Hostname: ");
        Serial.print(MDNS.hostname(i));
        Serial.print(" | IP: ");
        Serial.println(MDNS.address(i).toString());
        // ------------------------

        // LOOSER MATCHING: Check if it *contains* "quart-master" instead of exact match
        String foundName = MDNS.hostname(i);
        foundName.toLowerCase(); // handle case sensitivity
        
        if (foundName.indexOf("quart-master") >= 0) { 
          server_ip = MDNS.address(i).toString();
          Serial.println("MATCH FOUND! Server IP is: " + server_ip);
          
          // --- PERFORM HTTP CHECK ---
          HTTPClient http;
          http.setTimeout(5000);
          String url = "http://" + server_ip + ":8080/health";
          Serial.println("Ping URL: " + url);
          
          http.begin(url);
          int httpCode = http.GET();

          if (httpCode == 200) {
            Serial.println("Heartbeat: Server Verified! Disabling Recovery AP.");
            if (isRecoveryMode) {
              WiFi.softAPdisconnect(true);
              isRecoveryMode = false;
            }
            return; // Exit success
          } else {
            Serial.printf("Heartbeat: Server found but HTTP returned error: %d\n", httpCode);
          }
          http.end();
          break; // Stop looking after finding the match
        }
      }
    }
    
    // If we get here, either n=0 OR we looped through all services and found no match/bad HTTP
    Serial.println("Heartbeat Failed: Server NOT found or verified.");
    if (!isRecoveryMode) startRecoveryAP();

  } else {
    Serial.println("\nHeartbeat: WiFi Disconnected.");
    if (!isRecoveryMode) startRecoveryAP();
  }
}

void handleGetData() {
  // Security Check: Ensure the requester has the keys
  if (server.header("X-API-Key") != api_key || server.header("X-API-Secret") != api_secret) {
    server.send(401, "application/json", "{\"error\": \"Unauthorized\"}");
    return;
  }

  // Create a JSON response with the current state
  StaticJsonDocument<200> doc;
  doc["identity"] = DEVICE_TYPE;
  doc["value"] = value;
  doc["ip"] = WiFi.localIP().toString();

  String response;
  serializeJson(doc, response);
  server.send(200, "application/json", response);
}

void handlePairing() {
  Serial.println("Pairing Started.");
  
  // 1. Deserialize the Incoming Data
  StaticJsonDocument<400> doc;
  deserializeJson(doc, server.arg("plain"));

  // 2. Save Credentials to Flash Memory
  prefs.putString("ssid", doc["ssid"].as<String>());
  prefs.putString("pass", doc["pass"].as<String>());
  prefs.putString("api_key", doc["api_key"].as<String>());
  prefs.putString("api_secret", doc["api_secret"].as<String>());
  
  // Optional: Save server_ip (even though we use mDNS now, it's good as a backup)
  if (doc.containsKey("server_ip")) {
    prefs.putString("server_ip", doc["server_ip"].as<String>());
  }

  // 3. Generate the Unique Hostname (Network ID)
  // This logic must match exactly what you have in setup()
  String uniqueHostname = "esp32-" + String((uint32_t)ESP.getEfuseMac(), HEX);

  // 4. Create the JSON Response
  // We MUST send 'mdns_id' back so Python knows who to look for
  StaticJsonDocument<200> responseDoc;
  responseDoc["status"] = "Paired";
  responseDoc["identity"] = DEVICE_TYPE;
  responseDoc["mdns_id"] = uniqueHostname; 

  String response;
  serializeJson(responseDoc, response);

  // 5. Send and Restart
  Serial.print("Sending Pairing Response: ");
  Serial.println(response);
  
  server.send(200, "application/json", response);
  
  delay(2000);
  ESP.restart();
}



void handleUpdate() {
  Serial.println("Update has been requested.\n");
  if (server.header("X-API-Key") != api_key || server.header("X-API-Secret") != api_secret) {
    server.send(401, "text/plain", "Unauthorized");
    return;
  }

  StaticJsonDocument<200> doc;
  deserializeJson(doc, server.arg("plain"));
  value = doc["new_value"].as<String>();
  prefs.putString("value", value);
  Serial.println("Update has been succesful.\n");
  server.send(200, "text/plain", "Updated: " + value);
}


void setup() {
  Serial.begin(115200);
  prefs.begin("iot-config", false);

  ssid = prefs.getString("ssid", "");
  pass = prefs.getString("pass", "");
  api_key = prefs.getString("api_key", "");
  api_secret = prefs.getString("api_secret", "");
  server_ip = prefs.getString("server_ip", "");
  value = prefs.getString("value", "None");

  WiFi.begin(ssid.c_str(), pass.c_str());

String uniqueHostname = "esp32-" + String((uint32_t)ESP.getEfuseMac(), HEX); // e.g., "esp32-4A123F"

if (MDNS.begin(uniqueHostname.c_str())) { 
    MDNS.addService("http", "tcp", 80);
    // IMPORTANT: Add a TXT record so Python can verify the identity during pairing
    MDNS.addServiceTxt("http", "tcp", "identity", DEVICE_TYPE);
}
  
  int counter = 0;
  while (WiFi.status() != WL_CONNECTED && counter < 20) {
    delay(500); Serial.print("."); counter++;
  }

  if (WiFi.status() != WL_CONNECTED) {
    startRecoveryAP();
  } else {
    Serial.println("\nConnected! IP: " + WiFi.localIP().toString());
  }

  server.on("/config", HTTP_POST, handlePairing);
  server.on("/update", HTTP_POST, handleUpdate);
  server.on("/get-data", HTTP_POST, handleGetData);
  const char * headerkeys[] = {"X-API-Key", "X-API-Secret"};
  server.collectHeaders(headerkeys, 2);
  server.begin();
}

void loop() {
  server.handleClient();

  if (millis() - lastPingTime > PING_INTERVAL) {
    checkHeartbeat();
    lastPingTime = millis();
  }
}