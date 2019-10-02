import socket
import time
import sys
import os
from threading import Thread

sent = 0
size_of_file = 0

class ShowProgress(Thread):
    def __init__(self):
        super().__init__(daemon=True)

    def run(self):
        while True:
            time.sleep(0.2)
            print('progress: ' + str(int(1000 * sent / size_of_file) / 10) + '%')


file_name, addr, port_st = sys.argv[1], sys.argv[2], sys.argv[3]

port = int(port_st)

s = socket.socket()
s.connect((addr,port))
f = open (file_name, "rb")

encoded_s = bytes(file_name, 'utf-8')

kb = bytearray()

for i in range(1024 - len(encoded_s)):
    kb.append(0)

kb += encoded_s

size_of_file = os.path.getsize(file_name)

ShowProgress().start()

sent = 0

s.send(kb) # send name of file with 0-bytes in the beginning

sent = 1024

l = f.read(1024)
while (l):
    s.send(l)
    l = f.read(1024)
    sent += 1024
s.close()
