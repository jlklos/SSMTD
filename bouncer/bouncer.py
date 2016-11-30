from flask import Flask, abort, request
import requests
import random
import sys
import threading
app = Flask(__name__)

#either other remote bouncers or the endpoint
hosts = ['35.162.184.231:8888']

@app.route('/', methods=['POST'])
def bounce():
	def nextbounce(json):
		requests.post("http://%s"%random.choice(hosts), json=json)
		return

	print "Got something"
	if not request.json:
		return abort(400)
	t= threading.Thread(target=nextbounce, args=(request.json, ))
	t.start()
	return 'ok'

#you will need to supply the port number you want this to run on as an argument. 
if __name__ == "__main__":
	app.run(port=int(sys.argv[1]), host="0.0.0.0", debug=False)
