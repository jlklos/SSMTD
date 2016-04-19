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
                            

import threading
import argparse
import sys
import socket

parts = []
finish = []

class ClientThread(threading.Thread):

    def __init__(self, clientsock, chunksize, idx):
        threading.Thread.__init__(self)
        self.clientsock = clientsock
        global parts
        global finish
        self.chunksize = chunksize
        self.idx = idx

    def run(self):
        # get address of machine connecting to the HOST
        l = self.clientsock.recv(self.chunksize)
        # first packet recieved & loop to get the rest
        while l:
            print "Receiving messages"
            parts.append(l)
            print l
            #l = None 
            l = self.clientsock.recv(self.chunksize)
            if not l: break
            # recieve chunks and save them in parts        

        finish[self.idx] = 1 #indicate that the thread is finished recieving

# receive program
class listener():
    def __init__(self, port, chunksize):
        self.chunksize = chunksize
        global parts
        global finish
        self.threads = []
        self.port = port
        self.threadNum = 0

    def listening(self): 
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            # setting up the socket for the listener
            print 'Listener socket created, Hit Me!!!!!'
            s.bind(('0.0.0.0', self.port))
            # bind to the port and listen for a computer to connect
        except socket.error as msg:
            print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
            sys.exit()

        T = True
        while T != False:
            # start listening on socket port
            s.listen(5)
            print 'Socket now listening'        
            (clientsock, (addr, self.port)) = s.accept()
            print addr
            
            thread = ClientThread( clientsock, self.chunksize, self.threadNum )
            finish.append(0)
            self.threadNum = self.threadNum + 1
            thread.start()
            self.threads.append(thread)

            for i in finish:
                if i == 0:
                    T = True
                    break
                else:
                    T = False

        for j in self.threads:
            j.join()


        print "Done Receiving chunks"
        #conn.close()
        # close connection with client
        s.shutdown(socket.SHUT_RDWR)
        s.close()

class reassemble(threading.Thread):
    def __init__(self, fileToRec):
        global parts
        self.fileToRec = fileToRec

    # taking parts that were sent and reordering them to create a file
    def remake(self):
        for i in range(len(parts)):
            nullcount = 0
            if parts[i] == '\0':
                nullcount+=1
            print nullcount

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

def main():
    """
    Main program to call classes and class functions
    """
    parts = listener(args.port, args.chunk)
    parts.listening()
    reass = reassemble(args.fileToRec)
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
