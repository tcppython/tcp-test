import sys
import asyncore
import socket
import threading
import time
import signal
import os

# Global byte counter
bytes = []
bytes.append(0)
connections = []
connections.append(0)

class DevNullHandler(asyncore.dispatcher_with_send):
   
    global_bytes = bytes

    def handle_read(self):
        self.global_bytes[0] += len(self.recv(1024))

    def handle_close(self):
        self.close()

class Server(asyncore.dispatcher):
    "Receive connections and allocate a handler to each connection"

    handler = DevNullHandler
    global_connections = connections

    def __init__(self, host, port):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind((host, port))
        self.listen(5)

    def handle_accept(self):
        pair = self.accept()
        if pair is not None:
            sock, addr = pair
            print ("Incoming connection from %s" % repr(addr))
            self.global_connections[0] += 1
            handler = self.handler(sock)

def usage():
    print ("Usage: %s [<ip>:]<port>" % sys.argv[0])
    print ("")
    print ("If no IP is provided, 0.0.0.0 will be used")

if __name__ == '__main__':
    if len(sys.argv) == 1:
        usage()
        sys.exit()

    ip = "0.0.0.0"
    if ":" in sys.argv[1]:
        ip, port = sys.argv[1].split(":")
    else:
        port = sys.argv[1]
    port = int(port)

    server = Server(ip, port)
    print ("Listening on %s:%d..." % (ip, port))

    class report_thread(threading.Thread):
        def __init__(self, event):
            threading.Thread.__init__(self)
            self.stopped = event
            self.report_interval = 5.0

        def run(self):
            while not self.stopped.isSet():
                last_conns = connections[0]
                last_bytes = bytes[0]
                self.stopped.wait(self.report_interval)
                this_conns = connections[0]
                this_bytes = bytes[0]
                self.report(this_bytes - last_bytes, this_conns - last_conns)

        def report(self, diff_bytes, diff_conns):
            print ("%d connections/sec, %.2f KB/sec" %
                #len(server._map) - 1,
                diff_conns / 5.0,
                float(diff_bytes) / float(self.report_interval) / 1024.0,
            )

    stop_flag = threading.Event()
    t = report_thread(stop_flag)

    try:
        t.start()
        asyncore.loop()
    except:
        stop_flag.set()
