#!/usr/bin/env python3
# fake_ntp_improved.py
import socket, struct, time, sys

HOST = '0.0.0.0'
PORT = 123
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
print(f"Fake NTP server listening on {HOST}:{PORT} OFFSET={OFFSET}s")

while True:
    data, addr = s.recvfrom(1024)
    if not data or len(data) < 48:
        print("Ignored short packet from", addr); continue

    client_tx = data[40:48]  # client's Transmit Timestamp

    recv_time = time.time()
    tx_time = recv_time + OFFSET

    # Build parts
    rx_sec, rx_frac = unix_to_ntp_parts(recv_time)
    tx_sec, tx_frac = unix_to_ntp_parts(tx_time)
    ref_sec, ref_frac = unix_to_ntp_parts(tx_time - 5)  # reference = tx_time - 5s

    # sensible root delay/dispersion in NTP fixed-point (16.16)
    # e.g., 0.05 sec -> 0.05 * 2^16 = ~3277
    root_delay = int(0.05 * (1 << 16)) & 0xFFFFFFFF
    root_disp = int(0.05 * (1 << 16)) & 0xFFFFFFFF

    pkt = bytearray(48)

    pkt[0] = (0 << 6) | (3 << 3) | 4  # LI=0 VN=4 Mode=4
    pkt[1] = 1
    pkt[2] = 6
    pkt[3] = 0xFA  # precision -20

    struct.pack_into('!I', pkt, 4, root_delay)
    struct.pack_into('!I', pkt, 8, root_disp)
    struct.pack_into('!II', pkt, 12, ref_sec, ref_frac)

    pkt[24:32] = client_tx
    struct.pack_into('!II', pkt, 32, rx_sec, rx_frac)
    struct.pack_into('!II', pkt, 40, tx_sec, tx_frac)

    # debugging prints
    print("From:", addr)
    print("Client Transmit (req 40-47):", hex8(client_tx))
    print("Resp Originate (24-31):     ", hex8(pkt[24:32]), "==", pkt[24:32]==client_tx)
    print("Resp Receive (32-39):       ", hex8(pkt[32:40]))
    print("Resp Transmit (40-47):      ", hex8(pkt[40:48]))
    print("Ref Timestamp (12-19):      ", hex8(pkt[12:20]))
    print("Root delay/dispersion (4-11):", root_delay, root_disp)
    print("Human tx time:", time.ctime(tx_time))
    print("----")
    sys.stdout.flush()

    s.sendto(bytes(pkt), addr)
