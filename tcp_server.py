import socket

# =========================
# Configurazione
# =========================
LISTEN_IP = "0.0.0.0"
LISTEN_PORT = 5000

ACK_BYTE = b'\x06'

# =========================
# Utility stampa
# =========================
def format_data(data):
    hex_part = " ".join(f"{b:02X}" for b in data)
    ascii_part = "".join(chr(b) if 32 <= b < 127 else "." for b in data)
    return hex_part, ascii_part

# =========================
# Server TCP
# =========================
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind((LISTEN_IP, LISTEN_PORT))
sock.listen(1)

print(f"Server in ascolto su {LISTEN_IP}:{LISTEN_PORT}")

conn, addr = sock.accept()
print(f"Connessione da {addr}")

try:
    while True:
        data = conn.recv(1024)

        if not data:
            print("Connessione chiusa dal client")
            break

        hex_part, ascii_part = format_data(data)

        print("\n--- PACCHETTO RICEVUTO ---")
        print(f"Lunghezza: {len(data)} byte")
        print(f"HEX   : {hex_part}")
        print(f"ASCII : {ascii_part}")

        # Invio ACK
        conn.sendall(ACK_BYTE)

except KeyboardInterrupt:
    print("\nChiusura server")

finally:
    conn.close()
    sock.close()