#include <WiFi.h>

#if __has_include("secrets.h")
  #include "secrets.h"
#else
  #include "secrets_example.h"
#endif

// =========================
// Configuration
// =========================
#define TCP_PORT 5000

// CNC UART
#define CNC_RX 16
#define CNC_TX 17
#define CNC_BAUD 115200

// =========================
// MQTT ENABLE
// =========================
#define ENABLE_MQTT 0   // <-- set to 0 to completely disable

#if ENABLE_MQTT
  #include <PubSubClient.h>

  #define MQTT_BROKER "192.168.1.23"
  #define MQTT_PORT   1883
  #define MQTT_TOPIC  "esp32/cnc/log"

  WiFiClient espClient;
  PubSubClient mqtt(espClient);
#endif

// =========================
// Objects
// =========================
WiFiServer server(TCP_PORT);
WiFiClient tcpClient;

// =========================
// Utility functions
// =========================
void logMsg(const String &msg) {
  Serial.println(msg);

#if ENABLE_MQTT
  if (mqtt.connected()) {
    mqtt.publish(MQTT_TOPIC, msg.c_str());
  }
#endif
}

void connectWiFi() {
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  Serial.print("Connecting to WiFi");

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.printf("\nWiFi connected: %s\n", WiFi.localIP().toString().c_str());
}

#if ENABLE_MQTT
void connectMQTT() {
  while (!mqtt.connected()) {
    Serial.print("Connecting to MQTT...");
    if (mqtt.connect("ESP32-CNC")) {
      Serial.println("connected");
      logMsg("MQTT connected");
    } else {
      Serial.print("error, rc=");
      Serial.print(mqtt.state());
      Serial.println(" retry...");
      delay(2000);
    }
  }
}
#endif

// =========================
// Setup
// =========================
void setup() {
  Serial.begin(115200);
  Serial2.begin(CNC_BAUD, SERIAL_8N1, CNC_RX, CNC_TX);

  connectWiFi();

#if ENABLE_MQTT
  mqtt.setServer(MQTT_BROKER, MQTT_PORT);
#endif

  server.begin();
  logMsg("TCP server started");
}

// =========================
// Loop
// =========================
void loop() {

#if ENABLE_MQTT
  // Keep MQTT connected
  if (!mqtt.connected()) {
    connectMQTT();
  }
  mqtt.loop();
#endif

  // =========================
  // TCP client handling
  // =========================
  if (!tcpClient || !tcpClient.connected()) {
    tcpClient = server.accept();
    if (tcpClient) {
      logMsg("TCP client connected");
    }
  }

  if (!tcpClient || !tcpClient.connected()) return;

  // =========================
  // TCP → CNC (Serial2)
  // =========================
  if (tcpClient.available()) {
    uint8_t buf[256];
    int n = tcpClient.read(buf, sizeof(buf));
    if (n > 0) {
      Serial2.write(buf, n);
    }
  }

  // =========================
  // CNC → TCP
  // =========================
  if (Serial2.available()) {
    uint8_t buf[256];
    int n = 0;

    while (Serial2.available() && n < sizeof(buf)) {
      buf[n++] = Serial2.read();
    }

    tcpClient.write(buf, n);
  }
}
