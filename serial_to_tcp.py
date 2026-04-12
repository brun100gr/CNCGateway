import serial
import socket
import threading
import time

SERIAL_PORT = "/tmp/ttyV1"
BAUDRATE = 115200

TCP_IP = "127.0.0.1"
TCP_PORT = 5000

def log(direction, data):
    # testo (byte non stampabili diventano '.')
    text_data = ''.join(chr(b) if 32 <= b <= 126 else '.' for b in data)
    print(f"[{time.strftime('%H:%M:%S')}] {direction} | HEX: {hex_data} | TXT: {text_data}")

# =========================
# Setup seriale (con retry)
# =========================
while True:
    try:
        ser = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=0)
        print(f"Seriale aperta: {SERIAL_PORT}")
        break
    except serial.SerialException:
        print(f"Seriale non disponibile ({SERIAL_PORT}), retry tra 1s...")
        time.sleep(1)

# =========================
# Setup TCP (con retry)
# =========================
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

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
        try:
            data = ser.read(1024)
            if data:
                log("SER→TCP", data)
                sock.sendall(data)
        except Exception as e:
            print(f"Errore SERIAL→TCP: {e}")
            break

# =========================
# TCP → SERIAL
# =========================
def tcp_to_serial():
    while True:
        try:
            data = sock.recv(1024)
            if not data:
                print("Connessione chiusa dal server")
                break
            log("TCP→SER", data)
            ser.write(data)
        except Exception as e:
            print(f"Errore TCP→SERIAL: {e}")
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
    print("Chiusura gateway")
    sock.close()
    ser.close()
