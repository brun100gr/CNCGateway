import serial
import socket
import threading

SERIAL_PORT = "/tmp/ttyV2"
BAUDRATE = 115200

TCP_PORT = 5000

# =========================
# Setup
# =========================
ser = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=0)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(("0.0.0.0", TCP_PORT))
sock.listen(1)

print(f"Server in ascolto su {TCP_PORT}")
conn, addr = sock.accept()
print(f"Client connesso: {addr}")

# =========================
# TCP → SERIAL
# =========================
def tcp_to_serial():
    while True:
        data = conn.recv(1024)
        if not data:
            break
        ser.write(data)

# =========================
# SERIAL → TCP
# =========================
def serial_to_tcp():
    while True:
        data = ser.read(1024)
        if data:
            conn.sendall(data)

# =========================
# Threads
# =========================
t1 = threading.Thread(target=tcp_to_serial, daemon=True)
t2 = threading.Thread(target=serial_to_tcp, daemon=True)

t1.start()
t2.start()

try:
    while True:
        pass
except KeyboardInterrupt:
    print("Chiusura server")
    conn.close()
    sock.close()
    ser.close()