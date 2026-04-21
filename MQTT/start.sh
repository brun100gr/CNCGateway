#!/bin/sh

# avvia broker in background
mosquitto -c /mosquitto/config/mosquitto.conf &

sleep 2

echo "=== MQTT LOG LISTENER ==="

# sottoscrizione a tutti i topic
mosquitto_sub -h localhost -t "#" -v
