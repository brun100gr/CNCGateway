import serial
import socket
import time
import argparse

# =========================
# Argomenti CLI
# =========================
parser = argparse.ArgumentParser(description="Serial → TCP Gateway")

parser.add_argument(
    "--serial", "-s",
    default="/dev/ttyUSB0",
    help="Porta seriale (default: /dev/ttyUSB0)"
)

parser.add_argument(
    "--baudrate", "-b",
    type=int,
    default=115200,
    help="Baudrate seriale (default: 115200)"
)

parser.add_argument(
    "--max-size", "-m",
    type=int,
    default=128,
    help="Dimensione massima pacchetto (default: 128 byte)"
)

parser.add_argument(
    "--timeout", "-t",
    type=float,
    default=10,
    help="Timeout in millisecondi dall'ultimo byte (default: 10 ms)"
)

parser.add_argument(
    "--ip", "-i",
    default="127.0.0.1",
    help="IP server TCP (default: 127.0.0.1)"
)

parser.add_argument(
    "--port", "-p",
    type=int,
    default=5000,
    help="Porta server TCP (default: 5000)"
)

args = parser.parse_args()

# =========================
# Configurazione
# =========================
SERIAL_PORT = args.serial
BAUDRATE = args.baudrate
TCP_IP = args.ip
TCP_PORT = args.port

MAX_PACKET_SIZE = args.max_size
TIMEOUT_S = args.timeout / 1000.0  # ms → secondi

ACK_BYTE = b'\x06'

# =========================
# Setup seriale
# =========================
ser = serial.Serial(
    SERIAL_PORT,
    BAUDRATE,
    timeout=0
)

# =========================
# Setup TCP
# =========================
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((TCP_IP, TCP_PORT))

print("Gateway avviato")
print(f"Seriale: {SERIAL_PORT} @ {BAUDRATE}")
print(f"TCP: {TCP_IP}:{TCP_PORT}")
print(f"Max packet: {MAX_PACKET_SIZE} byte")
print(f"Timeout: {args.timeout} ms")

# =========================
# Funzione invio con ACK
# =========================
def send_with_ack(data):
    sock.sendall(data)

    ack = sock.recv(1)
    if ack != ACK_BYTE:
        raise Exception("ACK non valido ricevuto")

# =========================
# Loop principale
# =========================
buffer = bytearray()
last_byte_time = None

while True:
    data = ser.read(1)

    if data:
        buffer.extend(data)
        last_byte_time = time.time()

        if len(buffer) >= MAX_PACKET_SIZE:
            send_with_ack(buffer)
            buffer.clear()
            last_byte_time = None

    else:
        if buffer and last_byte_time:
            elapsed = time.time() - last_byte_time

            if elapsed >= TIMEOUT_S:
                send_with_ack(buffer)
                buffer.clear()
                last_byte_time = None