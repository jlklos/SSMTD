""" Program Name :	   send.py
	Program Overview : A Python program to break a file into multiple TCP streams and send them across multiple
					   network pathes. Requires the use of the recieve.py program to combine the TCP streams
					   back into a file.
	Program Version:   1.0.0
	Python Version:	   3.4.3
	Authors:		   Justin Soderstrom  <Justin.Soderstrom@trojans.dsu.edu>
					   Daniel Burwitz	 <Daniel.Burwitz@trojans.dsu.edu>
					   Evan Bolt		  <Evan.Bolt@trojans.dsu.edu>
	Date:			   April 1, 2016 (APRIL FOOLS!)
	Special Thanks:	   Argonne National Laboratory
					   Mike Shalanta
"""

import argparse
import os
import netifaces
import socket
import sys


class splitFile:
    'A class to split a file into equal size chunks'

    def __init__(self):
        self.fp = file(args.fileToSend, 'rb')
        self.fname, self.f_extension = os.path.splitext(args.fileToSend)
        self.stor = []
        self.count = 0


    def split(self):

        """
	    loops over a lambda which reads for args.b bytes,
	    then writes that to a file named by the current value of count.
	    While writing the file it appends the current value of count to the file
	    """
        for filePart in iter(lambda: self.fp.read(args.b), ''):
            # f = file(str(count),'wb')
            # stor[count].append = f.write(filePart+str(count))
            self.stor.append(filePart + '\0' + str(self.count))  # append null byte
            # f.close()
            self.count += 1
        f_ext = "\0" + self.f_extension # create string with null byte and file extension
        self.stor[self.count-1] += f_ext #append file extension to last file
        self.fp.close()


class send:
    'A class to send the file chunks over multiple network interfaces (LINUX ONLY)'

    def __init__(self, stor):
        self.stor = stor
        self.socketsList = []  # creates an empty list to hold each socket created
        self.ifaces = netifaces.interfaces()  # gathers a list of available network interfaces on local host

    def multiInterface(self):

        """
        Creates a client socket for each network interface on a multihomed linux machine.
        Program will use each socket to send file segments across different network pathes.
        """

        self.ifaces = [elem for elem in self.ifaces if elem[0:3] == "eth"]  # parses interface list for network adapters

        if len(self.ifaces) == 0:  # if there are no available network adapters on host, exit program
            print("No network interfaces available to send traffic. Exiting program...... ")
            sys.exit()
        elif len(self.ifaces) == 1:  # if there is only one available network adapter on host, ask to continue
            print("Only one adapter available to send traffic. MPTCP NOT GUARANTEED! Do you wish to continue (y/N)?")
            a = True
            while (a):  # continue to ask for a valid answer (y/N) until it is given by user
                cont = str(raw_input("Answer (y/N): "))
                if cont == 'y':
                    a = False
                elif cont == 'N':
                    sys.exit()
        # continue program normally if neither of the above conditions are met (interfaces >= 2)

        j = 0
        for i in self.ifaces:  # create a socket for each available network adapter and connects them to recieve node
            try:
                self.socketsList.append(socket.socket(socket.AF_INET, socket.SOCK_STREAM))  # create client socket
            except socket.error, msg:
                print("Failed to create socket. Error code: " + str(msg[0]) + " , Error message: " + msg[1])
                sys.exit()

            binder = netifaces.ifaddresses(i)[2][0]['addr']  # find ip address of network adapter
            self.socketsList[j].bind((binder, 0))  # bind socket to network adapter
            try:
                self.socketsList[j].connect((args.ipAddr, args.port))  # connects each socket to recieve node
            except socket.error:
                print("Could not connect to the destination node")
                sys.exit()

            """takes care of 'can't concatenate 'str' and 'int' object"""
            print("Socket %d successfully connected!" % j)
            j += 1

    def sendData(self):

        # Sends each file segment through all of the available network interfaces

        j = 0  # used to iterativly select a socket to send data, starting at index 0
        mod = len(self.socketsList)  # modulus to reset the j variable

        for i in self.stor:  # sends the file segments partially through each of the network adapters
            try:
                self.socketsList[j].sendall(i)  # sends the entire string of the file out a random interface
            except socket.error:  # error checking
                print("An error occured during sending the file. Quitting program...")
                sys.exit()
            j = j + 1 % mod  # used to select a socket to send data

        print("File sent successfully!")

        for i in self.socketsList: #closes out all sockets
            try: #attempts to shutdown and close every socket on all local interfaces
                i.shutdown(socket.SHUT_RDWR)
                i.close()
            except socket.error: # error checking
                print("Unable to gracefully shutdown sockets. Forcing shutdown now...")
                sys.exit()

def main():
    splitter = splitFile()
    splitter.split()
    sender = send(splitter.stor)
    sender.multiInterface()
    sender.sendData()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='A quick and dirty Multi-Path TCP using remote proxy hosts.')
    parser.add_argument('fileToSend', metavar='F', type=str, help='The file you would like to send.')
    parser.add_argument('ipAddr', metavar='I', type=str, help='The ip address of your destination node')
    parser.add_argument('-b', type=int, default=4096, help='The size of the blocks you want to split the file into.')
    parser.add_argument('-p', type=int, dest='port', default=5185, help='Change the port number for communication')

    args = parser.parse_args()

    main()
