#        Program Name : recieve.py
#        Program Overview : A Python program to recieve multiple TCP streams and reassemble
#                           them back into a file. Requires the use of the send.py program 
#                           to send the file into multiple TCP streams.
#        Program Version:   1.0.1
#        Python Version:    2.7.6
#        Authors:           Justin Soderstrom  <Justin.Soderstrom@trojans.dsu.edu>
#                           Daniel Burwitz     <Daniel.Burwitz@trojans.dsu.edu>
#                           Evan Bolt          <Evan.Bolt@trojans.dsu.edu>
#        Date:              April 18, 2016   
#        Special Thanks:    Argonne National Laboratory 
#!/usr/bin/env python                            

import time
import threading
import argparse
import sys
import socket
import SocketServer

#Global list that each thread appends file chunks
parts = []

class ThreadedTCPRequestHandler(SocketServer.BaseRequestHandler):

    def handle(self):
        global parts
        cur_thread = threading.current_thread()
        # get address of machine connecting to the HOST
        l = self.request.recv(self.server.chunksize)
        # first packet recieved & loop to get the rest
        self.timeout = time.time() + 5
        while l != '\0':
            if time.time() > self.timeout:
                print l
                parts.append(l)
                l = self.request.recv(self.server.chunksize)
            # recieve chunks and save them in parts
            else:
                break        
        print(str(cur_thread) +" has finished recieving messages")
        return 

class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass

class listener():
    def __init__(self, port, chunksize):
        self.chunksize = chunksize
        global parts
        self.HOST, self.PORT = '0.0.0.0', port
        
    def listening(self): 
        server = ThreadedTCPServer((self.HOST, self.PORT), ThreadedTCPRequestHandler)
        self.ip, self.port = server.server_address
        print("Listening on " + str(self.ip) + " with port " + str(self.port))
        server.chunksize = self.chunksize
        server_thread = threading.Thread(target=server.serve_forever) 
        # Creates a server thread that creates a thread for each request 
        server_thread.daemon = True
        server_thread.start()

        try:
            self.timeout = time.time() + 10 
            # time 10 secounds from now
            while threading.active_count() > 1: 
            #Waits until all threads are finished executing
                if time.time() > self.timeout:
                    server.shutdown() 
                    #shutsdown sever daemon
                    server.server_close()
                    break 
                    # break out of while loop after 10 secs.
        except KeyboardInterrupt:
            #kills the program on a keyboard interrupt (CTRL-C)
            print("Killing program...")
            server.shutdown()
            server.server_close()
            sys.exit()

        print("Finished recieving chunks...")

class reassemble():
    def __init__(self, fileToRec):
        global parts
        self.fileToRec = fileToRec

    # taking parts that were sent and reordering them to create a file
    def remake(self):
        print("Start remake")

        fp = open(self.fileToRec, 'wb')
        # opening the file to receive
        for fileParts in range(len(parts)):
            fp.writelines(parts[fileParts])
            # order and write the parts in the correct order to the file
        fp.close()
        print "Finish remake"
        f = open(self.fileToRec, 'r')
        # open the file so it can read from it
        file_contents = f.read()
        # printing the file
        print(file_contents)
        f.close()

def main():
    """
    Main program to call classes and class functions
    """
    parts = listener(args.port, args.chunk)
    parts.listening()
    reass = reassemble(args.fileToRec)
    reass.remake()
    sys.exit()

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
