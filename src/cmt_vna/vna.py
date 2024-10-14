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

    @property
    def id(self):
        self.s.sendall(b"*IDN?\n")
        return self.s.recv(4096).decode()

    def calibrate_OSL(self):
        standards = {"open": "OPEN", "short": "SHOR", "load": "LOAD"}
        for name, code in standards.items():
            print(f"Connect {name} standard, then press enter")
            input()
            cmd = f"SENS:CORR:COLL:{code} 1\n"
            self.s.sendall(cmd.encode())
            self.s.sendall(b"*OPC?\n")  # wait for operation complete
            print(self.s.recv(4096).decode())

        self.s.sendall(b"SENS:CORR:COLL:METH:SOLT1 1\n")
        self.s.sendall(b"SENS:CORR:COLL:SAVE\n")

    def transfer_data(self):
        raise NotImplementedError
