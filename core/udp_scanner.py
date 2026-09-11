# ==========================================
# 📌 Module 2 — UDP Scanner
# ==========================================



import socket

def scan_udp_port(host, port, timeout=1):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(timeout)

        s.sendto(b"", (host, port))

        try:
            data, addr = s.recvfrom(1024)
            return port
        except socket.timeout:
            return None
    except:
        return None
