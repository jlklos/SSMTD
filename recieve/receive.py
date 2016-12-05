from flask import Flask, request, abort
import base64
import time
import sys
import threading

app = Flask(__name__)
@app.route('/', methods=['POST'])
def receive():
	#here we wirte the received data to a file offset on the disk
	def _write(data, offsset, filename):
		#open it as a "read + write binary" file which will ensure
		#we don't null out parts of the file which would hapen if
		#we used used "wb"
		with open(filename,'r+b') as fp:
			#seek to the offset in the file
			fp.seek(int(offsset))
			#write the data
			fp.write(base64.b64decode(data))
			#make sure that data is written
			fp.flush()
		return
	#debug
	#print "Getting Stuff"
	#make sure the request is formatted as JSON, if it isn't abort
	if not request.json:
		return abort(400)
	#create the thread object, we are using a thread here to ensure that the host can continue sending things
	#(otherwise the host would have to wait the file wrote so that each host down the line
	#could then send OK back to the next host etc.)
	t= threading.Thread(target=_write, args=(request.json['data'],request.json['index'], sys.argv[1]))
	#start the thread
	t.start()
	return 'ok'

def main():
	app.run(port=8887, host='0.0.0.0', debug=False)

if __name__ == '__main__':
	main() 
