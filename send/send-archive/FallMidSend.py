#	Program Name :	   FallMidSend.py
#	Program Overview : A Python program to break a file into multiple TCP streams and send them across multiple
#			   network pathes. Requires the use of the FinalReceive.py program to combine the TCP streams
#			   back into a file. Also requires that computer is a Linux Debian distro and is multihomed to different
#                          network segments. Does not have funcationality for non-wired adapters i.e. WLAN adapters.
#	Program Version:   0.9.0
#	Python Version:	   2.7.6
#	Primary Author:	   Jacob Williams  <Jacob.Williams@trojans.dsu.edu>
#	Coauthors:         Daniel Burwitz     <Daniel.Burwitz@trojans.dsu.edu>
#
#	Date:		   October 25, 2016
#	Special Thanks:	   Argonne National Laboratory
#       Notes:             THIS IS A WORKING VERSION, NOT A FULL IMPLEMENTATION. Default Connection Port: 5185
#                          Default Chunksize: 4096 bytes. See the program documentation for more details.
#       #!/usr/bin/env python

import argparse
import os
import netifaces
import socket
import sys
import base64

class splitFile:
    'A class to split a file into equal size chunks'

    def __init__(self, fileToSend, block):
        self.fp = file(fileToSend, 'rb')
        self.fname, self.f_extension = os.path.splitext(fileToSend)
        self.stor = []
        self.count = 0
        self.block = block

    def split(self):
        """
        loops over a lambda which reads for self.block bytes,
        then writes that to a file named by the current value of count.
        While writing the file it appends the current value of count to the file
	"""

        for filePart in iter(lambda: self.fp.read(self.block), ''):
            self.stor.append(base64.b64encode(filePart) + ' ' + str(self.count))  # append null byte so recieve can know when to end
								# add a extra space at the end to change the log flow of recieve
            self.count += 1

        self.fp.close()
        #print self.stor

class First_Sock:

    def __init__(self, ipAddr, block):
	self.ipAddr = ipAddr	# IP Address
	self.block = block

    def sock(self): 			# generate size that we predict are sending at
	port = 7789
	size = self.block 		# getting chunk size
        string = "a"*size		# create string of a's as long as size
        base = base64.b64encode(string)	# encode so we can predict size
	lenbase = len(base) + 5		# add size of space and following number
        print lenbase
	strbase = str(lenbase)

	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	try:
		sock.connect((self.ipAddr, port))
		sock.send(strbase)		# send size predicted len
		sock.shutdown(socket.SHUT_RDWR)
                sock.close()
	except socket.error:
		print("Couldn't connect to the destination node")
                sys.exit()

class send:
    'A class to send the file chunks over multiple network interfaces (LINUX ONLY)'

    def __init__(self, stor, ipAddr, port, block, filetosend):
        self.stor = stor                        # stores all file segments
        self.socketsList = []  			# creates an empty list to hold each socket created
        self.ifaces = netifaces.interfaces()    # gathers a list of available network interfaces on local host
	self.ipAddr = ipAddr                    # pulls IP Address input
       	self.port = port                        # pulls in port number from input
	self.block = block			# size of the data we plan on sending
	self.filetosend = filetosend

    def multiInterface(self):
        """
        Creates a client socket for each network interface on a multihomed linux machine.
        Program will use each socket to send file segments across different network pathes.
        """

        self.ifaces = [elem for elem in self.ifaces if elem[0:3] == "eth" or elem[0:4] == "wlan"] # parses interface list for network adapters

        if len(self.ifaces) == 0:		   # if there are no available network adapters on host, exit program
            print("No network interfaces available to send traffic. Exiting program...... ")
            sys.exit()
        elif len(self.ifaces) == 1:		   # if there is only one available network adapter on host, ask to continue
            print("Only one adapter available to send traffic. MPTCP NOT GUARANTEED! Do you wish to continue (Y/N)?")
            a = True
            while (a):  			   # continue to ask for a valid answer (Y/N) until it is given by user
                cont = str(raw_input("Answer (Y/N): "))
                if cont == 'Y':
                    a = False
                elif cont == 'N':
                    sys.exit()
	print self.ifaces

        # continue program normally if neither of the above conditions are met (interfaces >= 2)

        j = 0
        for i in self.ifaces:     	     # create a socket for each available network adapter and connects them to recieve node

             networkFile = open('/sys/class/net/'+str(i)+'/operstate', 'r')                 # checks if an interface is active
             ethStat = networkFile.read(2)

             if ethStat == 'up':
                try:
                      self.socketsList.append(socket.socket(socket.AF_INET, socket.SOCK_STREAM))  # create client socket
                except socket.error, msg:
                      print("Failed to create socket. Error code: " + str(msg[0]) + " , Error message: " + msg[1])
                      sys.exit()

                binder = netifaces.ifaddresses(i)[2][0]['addr']                              # find ip address of network adapter
                self.socketsList[j].bind((binder, 0))                                        # bind socket to network adapter

                try:
		    print "im here"
                    self.socketsList[j].connect((self.ipAddr, self.port))                    # connects each socket to recieve node
                except socket.error:
                    print("Could not connect to the destination node")
                    sys.exit()

                print("Socket %d successfully connected!" % j)

                j = j + 1

             networkFile.close()

    def sendData(self):
        """
	Sends each file segment through all of the available network interfaces
	"""
	fileinfo = os.stat('self.filetosend')
	print fileinfo
	base =  fileinfo.st_size / self.base
	# length of file/ blocks
	print base
	strbase = str(base)
	# make it a string and grab length
	lenbase = len(strbase)
	print lenbase
	# prepend length amount of 0's to #
	for i in self.stor:
		try:
			self.stor
		        j = 0  					# used to iterativly select a socket to send data, starting at index 0
        		mod = len(self.socketsList)  		# modulus to reset the j variable
		except socket.error:
			sys.exit()

	for i in self.stor:				# sends the file segments partially through each of the network adapters
        	try:
			self.stor(i).rjust(lenbase, '0')
			self.socketsList[j].sendall(i)  # sends the entire string segment of the file out a random interface
			print(self.socketsList[j].sendall(i))
        	except socket.error:  		# error checking
                	print("An error occured during sending the file. Quitting program...")
                	sys.exit()

        j = (j + 1) % mod  			# used to select a socket to send data
        print("File sent successfully!")

        for i in self.socketsList: 		# closes out all sockets
            try: 				# attempts to shutdown and close every socket on all local interfaces
                i.shutdown(socket.SHUT_RDWR)
                i.close()
            except socket.error: 		# error checking
                print("Unable to gracefully shutdown sockets. Forcing shutdown now...")
                sys.exit()

def main():
    """
    Main program to perform full functionality of the program in a standalone
    enviroment
    """
    splitter = splitFile(args.fileToSend, args.b)
    splitter.split()
    sends = First_Sock(args.ipAddr, args.b)
    sends.sock()
    sender = send(splitter.stor, args.ipAddr, args.port, args.b, args.filetosend)
    sender.multiInterface()
    sender.sendData()

if __name__ == '__main__':
    """
    Creates passable arguments to set the file to send, ip address of the destination, block size to split the file chunks, 
    and port number of the destination host is listening on. The file to send and ip address are the only arguments that
    are required, while the block size and port number are optional arguments. The defaults for the block size is 4096 bytes
    and the default port number is 5185.
    """
    parser = argparse.ArgumentParser(description='Multipath TCP Proof-of-Concept implementation using multihomed Linux distros.')
    parser.add_argument('fileToSend', metavar='F', type=str, help='The file you would like to send.')
    parser.add_argument('ipAddr', metavar='I', type=str, help='The ip address of your destination node.')
    parser.add_argument('-b', type=int, default=4096, help='The size of the blocks you want to split the file into.')
    parser.add_argument('-p', type=int, dest='port', default=5185, help='Change the port number for communication.')

    args = parser.parse_args()

    main()
