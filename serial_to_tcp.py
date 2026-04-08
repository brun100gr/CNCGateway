import serial
import socket
import threading
import time

SERIAL_PORT = "/tmp/ttyV1"
BAUDRATE = 115200

TCP_IP = "127.0.0.1"
TCP_PORT = 5000

# =========================
# Setup
# =========================
ser = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=0)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

while True:
    try:
        sock.connect((TCP_IP, TCP_PORT))
        print("Connesso al server")
        break
    except ConnectionRefusedError:
        print("Server non disponibile, retry tra 1s...")
        time.sleep(1)

print("Gateway connesso")

# =========================
# SERIAL → TCP
# =========================
def serial_to_tcp():
    while True:
        data = ser.read(1024)
        if data:
            sock.sendall(data)

# =========================
# TCP → SERIAL
# =========================
def tcp_to_serial():
    while True:
        data = sock.recv(1024)
        if not data:
            break
        ser.write(data)

# =========================
# Threads
# =========================
t1 = threading.Thread(target=serial_to_tcp, daemon=True)
t2 = threading.Thread(target=tcp_to_serial, daemon=True)

t1.start()
t2.start()

try:
    while True:
        pass
except KeyboardInterrupt:
    print("Chiusura gateway")
    sock.close()
    ser.close()
