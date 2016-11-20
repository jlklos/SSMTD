from flask import Flask, request, abort
import base64
import time
import sys

app = Flask(__name__)
parts = {}
maxParts = None

@app.route('/', methods=['POST'])
def receive():
	print "Getting Stuff"
	global parts
	global maxParts
	if not request.json:
		return abort(400)
	if 'maxParts' in request.json:
		maxParts = int(request.json['maxParts'])
		if maxParts != None:
			if len(parts) == maxParts+1:
				time.sleep(1)
				with open(sys.argv[1],'wb') as fp:
					for index in xrange(0,len(parts)):
						fp.write(parts[index])
		return 'ok'
	else:
		parts[int(request.json['index'])] = base64.b64decode(request.json['data'])
		if maxParts != None:
			if len(parts) == maxParts+1:
				time.sleep(1)
				with open(sys.argv[1],'wb') as fp:
					for index in xrange(0,len(parts)):
						fp.write(parts[index])
		return 'ok'

def main():
	app.run(port=8888, host='0.0.0.0', debug=False)

if __name__ == '__main__':
	main()  
