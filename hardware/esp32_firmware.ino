#include <WiFi.h>
#include <HTTPClient.h>

// --- 1. Network Credentials ---
// Change these to your mobile hotspot's name and password
const char* ssid = "project";
const char* password = "project.123";

// --- 2. Edge Server Address ---
// This MUST be your laptop's local IPv4 address on the hotspot network!
const char* serverName = "http://10.161.99.56:8000/ingest";

// --- 3. Hardware Pin Definitions ---
const int mq7Pin = 34;      // Analog pin for CO Sensor
const int mq4Pin = 35;      // Analog pin for Methane Sensor
const int buzzerPin = 25;   // Digital pin for the local alarm
const int redLedPin = 26;   // Digital pin for Danger Status
const int greenLedPin = 27; // Digital pin for Network/Heartbeat Status

const float MQ7_DANGER_THRESHOLD = 50.0;

void setup() {
  Serial.begin(115200);
  pinMode(buzzerPin, OUTPUT);
  pinMode(redLedPin, OUTPUT);
  pinMode(greenLedPin, OUTPUT);

  // Initialize Wi-Fi Connection
  WiFi.begin(ssid, password);
  Serial.println("Connecting to Wi-Fi...");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nSuccessfully Connected to Wi-Fi!");
  digitalWrite(greenLedPin, HIGH); // Turn on green LED to show system is live
}

void loop() {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;

    // 1. Read Raw Analog Values (12-bit ADC: 0 to 4095)
    int rawMQ7 = analogRead(mq7Pin);
    int rawMQ4 = analogRead(mq4Pin);

    // 2. Convert to PPM (Simplified calculation for demonstration)
    // Note: True industrial calibration uses specific load resistor log curves
    float ppmMQ7 = rawMQ7 * (100.0 / 4095.0); 
    float ppmMQ4 = rawMQ4 * (50.0 / 4095.0);
    float temp = 30.5; // Placeholder (Can integrate DHT11 library here)
    float hum = 55.0;  // Placeholder 

    // 3. Local Hardware Reaction (The "Reactive" Buzzer)
    if (ppmMQ7 >= MQ7_DANGER_THRESHOLD) {
      digitalWrite(buzzerPin, HIGH);
      digitalWrite(redLedPin, HIGH);
    } else {
      digitalWrite(buzzerPin, LOW);
      digitalWrite(redLedPin, LOW);
    }

    // 4. Construct the JSON Payload Manually
    String jsonPayload = "{";
    jsonPayload += "\"mq7_ppm\": " + String(ppmMQ7) + ",";
    jsonPayload += "\"mq4_ppm\": " + String(ppmMQ4) + ",";
    jsonPayload += "\"temperature\": " + String(temp) + ",";
    jsonPayload += "\"humidity\": " + String(hum);
    jsonPayload += "}";

    // 5. Transmit Data via HTTP POST
    http.begin(serverName);
    http.addHeader("Content-Type", "application/json");

    int httpResponseCode = http.POST(jsonPayload);

    Serial.print("HTTP Response Code: ");
    Serial.println(httpResponseCode); // A '200' means FastAPI caught it perfectly!
    Serial.println("Sent: " + jsonPayload);

    http.end();
  } else {
    Serial.println("Wi-Fi Disconnected. Attempting to reconnect...");
    digitalWrite(greenLedPin, LOW);
  }

  // 6. The Refresh Cycle
  // Wait 5 seconds before reading and sending again (Aligns with Streamlit polling)
  delay(5000);
}