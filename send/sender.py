import argparse #used for parsing the arguments  
import base64 #used to encode the file so that binary files aren't garbled in transmision
"""requests (an HTTP client lib) is used to send the information to the bouncer (and then form the bouncer to the client/other bouncers)
while raw TCP sockets could have been used to transfer the information (and was used for the first implmentation) in the end a RESTful style HTTP
client server archatechure was chosen to act as our method of transport. This desition was made for a few reasions I will :
1) to send information ot the bouncers sockets could have been used but this was far quicker to prototype"""
import requests 
import random
import os #for getting the size of the file

#the remote bouncers that you want to hit
remoteHosts = ['169.254.142.143:8888','169.254.142.143:8889']
"""A generator used to split the file into parts this allows us lazily read the file
and save on memory costs"""
def splitupFile(fileName, blockSize):
	#open the file, this is only done once as the generator will loop around in the for section
	fp = file(fileName)
	#here we create an iterable out of this lambda function which reads the file for a certan number of bytes
	#determine where in the filewe are
	offset=fp.tell()
	for filePart in iter(lambda: fp.read(blockSize), ''):
		#we base64 encode the filePart for transfer
		filePart = base64.b64encode(filePart)
		#here we calculate the offset that the client will need to write that part of the file at.
		yield (offset , filePart)
		#determine where in the filewe are
		offset=fp.tell()
def main():
	#debug
	print("Sending file")
	#inform the client how large the file will be mostly so that it knows when it can stop receiving
	randomHost = random.choice(remoteHosts)
	r = requests.post("http://%s" % randomHost, json={'filesize':str(os.path.getsize(args.fileToSend)),'blocksize':str(args.b)})
	#here we use for's ablity to unpack tuples to unpack the tuple we yield from splitupFile as it iterates through the file
	for offset, part in splitupFile(args.fileToSend, args.b):
		#setting up the json dict
		data = {'index':offset, 'data':part}
		#this is mostly me being lazy here I should have had a count % len(remoteHosts) so it would use each path equally but sue me I wrote this in an hour ;)
		randomHost = random.choice(remoteHosts)
		#here we get to the heart of the operation. the file is sent to the random host via POST encoded as a json blob
		r = requests.post("http://%s" % randomHost, json=data)
		#debug stuff don't worry about it
		print("Offset %d sent to %s" % (offset, randomHost))
		#we have covered this already
	print("Sending finished")
	randomHost = random.choice(remoteHosts)
	#r = requests.post("http://%s" % randomHost, json={'finished':''})

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='A quick and dirty Multi-Path TCP using remote proxy hosts.')
	parser.add_argument('fileToSend', metavar='F', type=str, help='The file you would like to send.')
	parser.add_argument('-b', type=int, default=4096, help='The size of the blocks you want to split the file into.' )
	args = parser.parse_args()
	main()
