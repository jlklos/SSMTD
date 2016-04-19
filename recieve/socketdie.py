import threading
import argparse
import sys
import socket

class ClientThread(threading.Thread):

    def __init__(self, clientsock, parts, chunksize):
        threading.Thread.__init__(self)
        self.clientsock = clientsock
        self.parts = parts
        self.chunksize = chunksize

    def run(self):
        # get address of machine connecting to the HOST
        l = self.clientsock.recv(self.chunksize)
        # first packet recieved & loop to get the rest
        while l:
            print "Receiving messages"
            self.parts.append(l)
            l = self.clientsock.recv(self.chunksize)
            if not l: break
            # recieve chunks and save them in parts        
        return self.parts

# receive program
class listener():
    def __init__(self, port, chunksize):
        self.chunksize = chunksize
        self.parts = []
        self.threads = []
        self.port = port

    def listening(self): 
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            # setting up the socket for the listener
            print 'Listener socket created'
            s.bind(('0.0.0.0', self.port))
            # bind to the port and listen for a computer to connect
        except socket.error as msg:
            print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
            sys.exit()

        while True:
            # start listening on socket port
            s.listen(5)
            print 'Socket now listening'        
            (clientsock, (addr, self.port)) = s.accept()
            print addr
            thread = ClientThread( clientsock, self.parts, self.chunksize )
            thread.start()
            self.threads.append(thread)

        for j in self.threads:
            j.join()


        print "Done Receiving chunks"
        conn.close()
        # close connection with client
        s.shutdown(socket.SHUT_RDWR)
        s.close()
        return self.parts

class reassemble(threading.Thread):
    def __init__(self, parts, fileToRec):
        self.parts = parts
        self.fileToRec = fileToRec

    # taking parts that were sent and reordering them to create a file
    def remake(self):
        for i in range(len(self.parts)):
            nullcount = 0
            if self.parts[i] == '\0':
                nullcount+=1
            print nullcount

        fp = open(self.fileToRec, 'wb')
        # opening the file to receive
        for fileParts in range(len(self.parts)):
            fp.writelines(self.parts[fileParts])
            # order and write the parts in the correct order to the file
        fp.close()
        print "Finish remake"
        f = open(self.fileToRec, 'r')
        # open the file so it can read from it
        file_contents = f.read()
        # printing the file
        print(file_contents)

def main():
    """
    Main program to call classes and class functions
    """
    parts = listener(args.port, args.chunk)
    parts.listening()
    reass = reassemble(parts.parts, args.filetoRec)
    reass.remake()


if __name__ == '__main__':
    """
    Creates passable arguments to set the file to send, block size, and port number to listen on.  Default block size is 4096,
    and default port number is 5185.  The only argument a user must always specify is the file name.
    """
    parser = argparse.ArgumentParser(description='Multipath TCP Proof-of-Concept implementation using multihomed Linux distros.')
    parser.add_argument('fileToRec', metavar='F', type=str, help='The file to receive from sender.')
    parser.add_argument('-b', dest='chunk', type=int, default=4096, help='The size of the blocks that have been split.')
    parser.add_argument('-p', dest='port', type=int, default=5185, help='Change the default communication port.')

    args = parser.parse_args()

    main()
