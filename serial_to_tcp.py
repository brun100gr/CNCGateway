import serial
import socket
import threading
import time

SERIAL_PORT = "/tmp/ttyV1"
BAUDRATE = 115200

ESP_NAME = "esp32.local"
TCP_PORT = 5000

def log(direction, data):
    # HEX
    hex_data = " ".join(f"{b:02X}" for b in data)

    # Readable ASCII (non-printable → '.')
    text_data = ''.join(chr(b) if 32 <= b <= 126 else '.' for b in data)

    print(f"[{time.strftime('%H:%M:%S')}] {direction} | HEX: {hex_data} | TXT: {text_data}")

# =========================
# Serial setup (with retry)
# =========================
while True:
    try:
        ser = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=0.1)
        print(f"Serial opened: {SERIAL_PORT}")
        break
    except serial.SerialException:
        print(f"Serial not available ({SERIAL_PORT}), retry in 1s...")
        time.sleep(1)

# =========================
# TCP setup (with retry)
# =========================
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

while True:
    try:
        sock.connect((ESP_NAME, TCP_PORT))
        print("Connected to server")
        break
    except ConnectionRefusedError:
        print("Server not available, retry in 1s...")
        time.sleep(1)

print("Gateway connected")

# =========================
# SERIAL → TCP
# =========================
def serial_to_tcp():
    while True:
        try:
            data = ser.read(1024)
            if data:
                log("SER→TCP", data)
                sock.sendall(data)
        except Exception as e:
            print(f"Error SERIAL→TCP: {e}")
            break

# =========================
# TCP → SERIAL
# =========================
def tcp_to_serial():
    while True:
        try:
            data = sock.recv(1024)
            if not data:
                print("Connection closed by server")
                break
            log("TCP→SER", data)
            ser.write(data)
        except Exception as e:
            print(f"Error TCP→SERIAL: {e}")
            break

# =========================
# Threads
# =========================
t1 = threading.Thread(target=serial_to_tcp, daemon=True)
t2 = threading.Thread(target=tcp_to_serial, daemon=True)

t1.start()
t2.start()

# =========================
# Main loop
# =========================
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Shutting down gateway")
    sock.close()
    ser.close()
