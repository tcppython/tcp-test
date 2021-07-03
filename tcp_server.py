import asyncore
import socket
import time

CONNECTIONS = 500
arr = [None] * CONNECTIONS

class Client(asyncore.dispatcher):
    host = "localhost"
    port = 25000
    mesg = "Hello World\n"

    def __init__(self):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect((self.host, self.port))

    def handle_connect(self):
        pass

    def handle_close(self):
        self.close()

    def handle_read(self):
        self.recv(4096)

    def writable(self):
        return True

    def handle_write(self):
        self.send(self.mesg)
        self.close()
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect((self.host, self.port))

for i in range(len(arr)):
    if not arr[i] or arr[i].closed():
        arr[i] = Client()

asyncore.loop()
