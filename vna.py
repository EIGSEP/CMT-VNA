import socket

IP = "127.0.0.1"
PORT = 5025

class VNA:

    def __init__(self, ip=IP, port=PORT):
        self.ip = ip
        self.port = port
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((self.ip, self.port))

    def __close__(self):
        self.s.close()
    
    def get_id(self):
        self.s.sendall(b"*IDN?\n")
        return self.s.recv(4096).decode()
