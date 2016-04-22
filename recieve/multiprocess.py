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
import argparse
import sys
import socket
import multiprocessing

#Global list that each thread appends file chunks
parts = []

def serviceConnect(clientsock, chunksize):
    p = multiprocessing.current_process()
    global parts

    l = clientsock.recv(chunksize)
    # set l to first thing that was sent
    while True:
          if l != "":
            l = clientsock.recv(chunksize)
            print l
            # append to parts so the it can be ressambled 
            parts.append(l)
          else:
            break
    # close clientsock out correcly 
    clientsock.shutdown(socket.SHUT_RDWR)
    clientsock.close()        
    print(str(p.name) + str(p.pid) + " has finished recieving messages")
    return 

class listener():
    def __init__(self, port, chunksize):
        self.chunksize = chunksize
        global parts
        self.processes = []
        self.port = port
        
    def listening(self): 
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#       s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.settimeout(5)

        print "Listener socket created"

        s.bind(('0.0.0.0', self.port))

        while True:
            try:
                s.listen(5)
                (clientsock, (clientaddr, clientport)) = s.accept()
                print ("Connection recieved from " + str(clientaddr) + " on port " + str(clientport))
                process = multiprocessing.Process(target = serviceConnect, args=(clientsock, self.chunksize))
                process.start()
                self.processes.append(process)
            except socket.timeout:
            # break out of while loop if nothing connects
                break

        s.shutdown(socket.SHUT_RDWR)
        s.close()
        # shutting down our sockets correctly
        for i in self.processes:
            i.join(1)
            if i.is_alive():
                i.terminate()
                i.join()

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
