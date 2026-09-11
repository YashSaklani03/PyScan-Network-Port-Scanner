import socket

def detect_service(port):
    try:
        return socket.getservbyport(port)
    except:
        return "unknown"
