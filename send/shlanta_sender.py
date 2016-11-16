import argparse
import base64
import requests
import random

#the remote bouncers that you want to hit
remoteHosts = ['192.168.0.254:8888','192.168.0.254:8889']

def splitupFile(fileName, blockSize):
	fp = file(fileName)
	count = 0
	for filePart in iter(lambda: fp.read(blockSize), ''):
		filePart = base64.b64encode(filePart)
		yield (count,filePart)
		count+=1

def main():
	data = {}
	print("Sending file")
	maxCount = 0
	for count, part in splitupFile(args.fileToSend, args.b):
		data = {'index':count, 'data':part}
		randomHost = random.choice(remoteHosts)
		r = requests.post("http://%s" % randomHost, json=data)
		print("Part %d sent to %s" % (count, random.choice(remoteHosts)))
		maxCount = count
	r = requests.post("http://%s" % randomHost, json={'maxParts':maxCount})
	print("Sending finished")


if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='A quick and dirty Multi-Path TCP using remote proxy hosts.')
	parser.add_argument('fileToSend', metavar='F', type=str, help='The file you would like to send.')
	parser.add_argument('-b', type=int, default=4096, help='The size of the blocks you want to split the file into.' )
	args = parser.parse_args()
	main()
