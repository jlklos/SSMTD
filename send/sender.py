import argparse #used for parsing the arguments  
import base64 #used to encode the file so that binary files aren't garbled in transmision
"""requests (an HTTP client lib) is used to send the information to the bouncer (and then form the bouncer to the client/other bouncers)
while raw TCP sockets could have been used to transfer the information (and was used for the first implmentation) in the end a RESTful style HTTP
client server archatechure was chosen to act as our method of transport. This desition was made for a few reasions I will :
1) to send information ot the bouncers sockets could have been used but this was far quicker to prototype"""
import requests # /\
import random #because I am lazy

#the remote bouncers that you want to hit
remoteHosts = ['192.168.0.254:8888','192.168.0.254:8889']
"""A generator used to split the file into parts this allows us lazily read the file
and save on memory costs"""
def splitupFile(fileName, blockSize):
	#open the file, this is only done once as the generator will loop around in the for section
	fp = file(fileName)
	#init the count which will let the client know where that part of the file should go
	count = 0
	#here we create an iterable out of this lambda function which reads the file for a certan number of bytes
	for filePart in iter(lambda: fp.read(blockSize), ''):
		#we base64 encode the filePart for transfer
		filePart = base64.b64encode(filePart)
		#yield the count and the peice of the file as a tuple
		yield (count,filePart)
		count+=1

def main():
	#data is a tempory variable used to store the dict that we will turn into the json blob we send
	data = {}
	print("Sending file")
	#because I am dumb and couldn't find a beter way of doing this (which is finding out the total
	#length of the file which we don't know till the end because of the lazy reading)
	maxCount = 0
	#here we use for's ablity to unpack tuples to unpack the tuple we yield from splitupFile as it iterates through the file
	for count, part in splitupFile(args.fileToSend, args.b):
		#setting up the json dict
		data = {'index':count, 'data':part}
		#this is mostly me being lazy here I should have had a count % len(remoteHosts) so it would use each path equally but sue me I wrote this in an hour ;)
		randomHost = random.choice(remoteHosts)
		#here we get to the heart of the operation. the file is sent to the random host via POST encoded as a json blob
		r = requests.post("http://%s" % randomHost, json=data)
		#debug stuff don't worry about it
		print("Part %d sent to %s" % (count, random.choice(remoteHosts)))
		#we have covered this already
		maxCount = count
	#send the maxCount to one of the bouncers tell the client when to stop receiving.
	r = requests.post("http://%s" % randomHost, json={'maxParts':maxCount})
	print("Sending finished")


if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='A quick and dirty Multi-Path TCP using remote proxy hosts.')
	parser.add_argument('fileToSend', metavar='F', type=str, help='The file you would like to send.')
	parser.add_argument('-b', type=int, default=4096, help='The size of the blocks you want to split the file into.' )
	args = parser.parse_args()
	main()
