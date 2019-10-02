import socket
import os
from threading import Thread


clients = []

# Thread to listen one particular client
class ClientListener(Thread):
    def __init__(self, name: str, sock: socket.socket):
        super().__init__(daemon=True)
        self.sock = sock
        self.name = name

    # add 'me> ' to sended message
    def _clear_echo(self, data):
        # \033[F – symbol to move the cursor at the beginning of current line (Ctrl+A)
        # \033[K – symbol to clear everything till the end of current line (Ctrl+K)
        self.sock.sendall('\033[F\033[K'.encode())
        data = 'me> '.encode() + data
        # send the message back to user
        self.sock.sendall(data)

    # broadcast the message with name prefix eg: 'u1> '
    def _broadcast(self, data):
        data = (self.name + '> ').encode() + data
        for u in clients:
            # send to everyone except current client
            if u == self.sock:
                continue
            u.sendall(data)

    # clean up
    def _close(self):
        clients.remove(self.sock)
        self.sock.close()
        print(self.name + ' disconnected')

    def run(self):
        while True:
            # try to read 1024 bytes from user
            # this is blocking call, thread will be paused here
            
            file_name_in_bytes = bytearray(self.sock.recv(1024))
            while (file_name_in_bytes[0] == 0):
                file_name_in_bytes.remove(0)

            file_name = file_name_in_bytes.decode('utf-8') # recieve name of file
            
            print('recieving: ', file_name)

            if os.path.exists('uploaded_files/' + file_name): # check if file already exists
                copy_number = 1

                ext = file_name[file_name.rfind('.') + 1:]
                file_name = file_name[:file_name.rfind('.')]
                
                file_name += '_copy_' + str(copy_number)
                while os.path.exists('uploaded_files/' + file_name + '.' + ext): # try name by name
                    file_name = file_name[:-len(str(copy_number))]
                    copy_number += 1
                    file_name += str(copy_number)
                    
                file_name += '.' + ext
                
            print('file will be saved as: ', file_name)

            f = open('uploaded_files/' + file_name, 'wb+')
            
            data = self.sock.recv(1024) # recieve file
            while (data):
                f.write(data)
                data = self.sock.recv(1024)

            f.close()
            # if we got no data – client has disconnected
            self._close()
            # finish the thread
            return


def main():
    next_name = 1

    # AF_INET – IPv4, SOCK_STREAM – TCP
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # reuse address; in OS address will be reserved after app closed for a while
    # so if we close and imidiatly start server again – we'll get error
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # listen to all interfaces at 8800 port
    sock.bind(('', 8800))
    sock.listen()
    while True:
        # blocking call, waiting for new client to connect
        con, addr = sock.accept()
        clients.append(con)
        name = 'u' + str(next_name)
        next_name += 1
        print(str(addr) + ' connected as ' + name)
        # start new thread to deal with client
        ClientListener(name, con).start()


if __name__ == "__main__":
    main()
