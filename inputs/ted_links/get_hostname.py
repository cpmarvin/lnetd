import socket

def get_hostname(ip):
    ip = str(ip)
    try:
        name = socket.gethostbyaddr(ip)[0]
    except Exception as e:
        name = -1
    return name
