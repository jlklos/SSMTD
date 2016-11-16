from flask import Flask, abort, request
import requests
import random
import sys
app = Flask(__name__)

#either other remote bouncers or the endpoint
hosts = ['192.168.0.254:8887']

@app.route('/', methods=['POST'])
def bounce():
	if not request.json:
		return abort(400)
	requests.post("http://%s"%random.choice(hosts), json=request.json)
	return 'ok'

#you will need to supply the port number you want this to run on as an argument. 
if __name__ == "__main__":
	app.run(port=int(sys.argv[1]), host="0.0.0.0", debug=False)