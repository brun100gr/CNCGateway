#include <WiFi.h>
#include <PubSubClient.h>

#if __has_include("secrets.h")
  #include "secrets.h"
#else
  #include "secrets_example.h"
#endif

// =========================
// Configurazione
// =========================
#define TCP_PORT 5000

// UART CNC (modifica se serve)
#define CNC_RX 16
#define CNC_TX 17
#define CNC_BAUD 115200

// MQTT
#define MQTT_BROKER "192.168.1.100"
#define MQTT_PORT   1883
#define MQTT_TOPIC  "esp32/cnc/log"

// =========================
// Oggetti
// =========================
WiFiServer server(TCP_PORT);
WiFiClient tcpClient;

WiFiClient espClient;
PubSubClient mqtt(espClient);

// =========================
// Funzioni utili
// =========================
void logMQTT(const String &msg) {
  Serial.println(msg);
  if (mqtt.connected()) {
    mqtt.publish(MQTT_TOPIC, msg.c_str());
  }
}

void connectWiFi() {
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  Serial.print("Connessione WiFi");

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.printf("\nWiFi connesso: %s\n", WiFi.localIP().toString().c_str());
}

void connectMQTT() {
  while (!mqtt.connected()) {
    Serial.print("Connessione MQTT...");
    if (mqtt.connect("ESP32-CNC")) {
      Serial.println("connesso");
      logMQTT("MQTT connesso");
    } else {
      Serial.print("errore, rc=");
      Serial.print(mqtt.state());
      Serial.println(" retry...");
      delay(2000);
    }
  }
}

// =========================
// Setup
// =========================
void setup() {
  Serial.begin(115200);
  Serial2.begin(CNC_BAUD, SERIAL_8N1, CNC_RX, CNC_TX);

  connectWiFi();

  mqtt.setServer(MQTT_BROKER, MQTT_PORT);

  server.begin();
  logMQTT("Server TCP avviato");
}

// =========================
// Loop
// =========================
void loop() {
  // Mantieni MQTT connesso
  if (!mqtt.connected()) {
    connectMQTT();
  }
  mqtt.loop();

  // Gestione client TCP
  if (!tcpClient || !tcpClient.connected()) {
    tcpClient = server.accept();
    if (tcpClient) {
      logMQTT("Client TCP connesso");
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
