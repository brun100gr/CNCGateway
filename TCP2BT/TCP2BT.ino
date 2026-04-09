#include <WiFi.h>
#include "BluetoothSerial.h"

#if __has_include("secrets.h")
  #include "secrets.h"
#else
  #include "secrets_example.h"
#endif

// =========================
// Configurazione
// =========================
#define TCP_PORT      5000
#define BT_DEVICE_NAME "ESP32-BT-Target"  // dispositivo BT a cui connettersi

BluetoothSerial SerialBT;
WiFiServer server(TCP_PORT);
WiFiClient client;

// =========================
// Setup
// =========================
void setup() {
  Serial.begin(115200);

  // Connessione WiFi
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  Serial.print("Connessione WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.printf("\nWiFi connesso, IP: %s\n", WiFi.localIP().toString().c_str());

  // Avvia server TCP
  server.begin();
  Serial.printf("Server TCP in ascolto su porta %d\n", TCP_PORT);

  // Avvia Bluetooth Classic (modalità master, connessione a dispositivo esterno)
  SerialBT.begin("ESP32-Bridge", true); // true = modalità master
  Serial.printf("Bluetooth avviato, connessione a \"%s\"...\n", BT_DEVICE_NAME);

  // Connessione al dispositivo BT (retry finché non riesce)
  while (!SerialBT.connect(BT_DEVICE_NAME)) {
    Serial.println("Connessione BT fallita, retry...");
    delay(1000);
  }
  Serial.println("Bluetooth connesso!");
}

// =========================
// Loop: bridge TCP ↔ BT
// =========================
void loop() {
  // Accetta nuovi client TCP se non ce n'è uno attivo
  if (!client || !client.connected()) {
    client = server.accept();
    if (client) {
      Serial.println("Client TCP connesso");
    }
  }

  if (!client || !client.connected()) return;

  // TCP → BT
  if (client.available()) {
    uint8_t buf[256];
    int n = client.read(buf, sizeof(buf));
    if (n > 0) {
      SerialBT.write(buf, n);
    }
  }

  // BT → TCP
  if (SerialBT.available()) {
    uint8_t buf[256];
    int n = 0;
    while (SerialBT.available() && n < sizeof(buf)) {
      buf[n++] = SerialBT.read();
    }
    client.write(buf, n);
  }
}