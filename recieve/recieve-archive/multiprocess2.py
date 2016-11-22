#        Program Name :     FinalRecieve.py
#        Program Overview : A Python program to recieve multiple TCP streams and reassemble
#                           them back into a file. Typically requires the use of the FinalSend.py program 
#                           to send the file into multiple TCP streams, but can service simple socket
#                           send requests.
#        Program Version:   0.9.0
#        Python Version:    2.7.6
#        Primary Author:    Justin Soderstrom  <Justin.Soderstrom@trojans.dsu.edu>
#        Coauthors:         Daniel Burwitz     <Daniel.Burwitz@trojans.dsu.edu>
#                           Evan Bolt          <Evan.Bolt@trojans.dsu.edu>
#        Last Update:       April 24, 2016   
#        Special Thanks:    Argonne National Laboratory 
#        Notes:             THIS IS A WORKING VERSION, NOT A FULL IMPLEMENTATION. Can accept and service incoming 
#                           TCP requests. However, it does not yet reassemble files in the correct order and 
#                           has trouble receiving small files. Please refer to the program documentation for
#                           further details. DEFAULT PORT: 5185 DEFAULT CHUNKSIZE: 4096 bytes 
#        !/usr/bin/env python                            

import argparse
import socket
import multiprocessing
import multiprocessing.reduction
import StringIO
import pickle

def forking_dumps(socket):
    # Used to serialize socket objects to be passed between multiple processes
    # Utilizes the StringIO and multiprocessing.reduction python libraries
    buffer = StringIO.StringIO()
    multiprocessing.reduction.ForkingPickler(buffer).dump(socket)
    return buffer.getvalue()

def serviceConnect(clientsocks, parts, chunksize):
    # Forked process code. Pulls an open client socket from the multiprogramming clientsocks queue.
    # From this socket, process recieves data and appends it to multiprogramming parts list for reassembly.

    # Used to print out process name and id
    p = multiprocessing.current_process()
    # Used to deserialize socket object from clientsocks queue
    sock = pickle.loads(clientsocks.get())
    # Starts to receive from the socket where it is listening 
    l = sock.recv(chunksize)
    while True:
          if l != "":
            l = sock.recv(chunksize)
            # append to parts list so the the file can be ressambled 
            parts.append(l)
          else:
            break      
    print(str(p.name) + str(p.pid) + " has finished recieving messages")
    return 

class listener():
    """
    Class used to listen for incoming TCP connections. When it receives a connection, the main process forks a 
    a child process to service that connection. Socket times out after 5 seconds and kills children processes
    if they have not finished their execution.
    """
    def __init__(self, port, chunksize):
        self.chunksize = chunksize
        self.processes = []
        self.port = port

    def listening(self): 
        # Create listener socket and set the socket timeout
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.settimeout(5)

        print("Listener socket created and listening...")

        # Bind the port to our network interface on port specified
        s.bind(('0.0.0.0', self.port))

        # Socket listens for 5 seconds and services incoming connections by forking children processes.
        while True:
            try:
                # Listen for incoming TCP connections
                s.listen(5)
                # Accept the connection
                (sock, (clientaddr, clientport)) = s.accept()
                print ("Connection recieved from " + str(clientaddr) + " on port " + str(clientport))
                # Serialize and place our new socket object into the clientsocks queue
                clientsocks.put(forking_dumps(sock))
                # Fork child process and pass it the clientsocks queue, parts list, and chunk size to receive
                process = multiprocessing.Process(target = serviceConnect, args=(clientsocks, parts, self.chunksize))
                process.start()
                # Append process object to processes list to keep track of it
                self.processes.append(process)
            except socket.timeout:
            # Break out of while loop when the socket times out
                break

        # Close out our listening socket
        s.shutdown(socket.SHUT_RDWR)
        s.close()

        # Shutting down our sockets correctly
        for i in self.processes:
            # Wait for 1 second to join the child process
            i.join(1)
            # If the child process is still alive, kill it and then join
            if i.is_alive():
                i.terminate()
                i.join()
        print("Closed listener socket...")

class reassemble():
    """
    Class used to reassemble the file chunks from the parts list after we have finished receiving our file chunks
    """
    def __init__(self, fileToRec):
        self.fileToRec = fileToRec

    # Taking parts that were sent and reordering them to create a file
    def remake(self):
        print("Start remake")

        fp = open(self.fileToRec, 'wb')
        # Opening the file to receive
        for fileParts in xrange(len(parts)):
            fp.writelines(parts[fileParts])
            # Order and write the parts in the correct order to the file
        fp.close()
        print("Finish remake")
        f = open(self.fileToRec, 'r')
        # Open the file so it can read from it
        file_contents = f.read()
        # Printing the file
        print(file_contents)
        f.close()

def main():
    """
    Main program to call classes and class functions. Shows how to correctly execute the program.
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

    # Creates multiprocessing queue to be used as a queue for socket objects
    clientsocks = multiprocessing.Queue()
    manager = multiprocessing.Manager() 
    # Uses multiprocessing manager to create a list that can be modified by children processes    
    parts = manager.list()   
    
    main()
