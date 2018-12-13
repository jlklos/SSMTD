from flask import Flask, abort, request # for receiving
import requests # or sending
import random # for picking the next hop
import sys # for arg parsing
import threading # used to ensure concurrent operation
app = Flask(__name__)

# either other remote bouncers or the endpoint
hosts = ['35.162.184.231:8888']

# here we tell it to do the decorated method when the root of the web
# server is requested
@app.route('/', methods=['POST'])
def bounce():
	# here we use a nested funtion to keep the namespace clean this
	# funciton is used by the thread to send data on to the next host
	def nextbounce(json, host):
		# here we send the data we recived off to the next hop
		requests.post("http://%s" % host, json=json)
		return
	# debug
	# print("Got something")
	# ensure the post contains JSON
	if not request.json:
		# if it doesn't contain JSON then abort
		return abort(400)
	# create the thread object, we are using a thread here to ensure
	# that the host can continue sending things (otherwise the host
	# would have to wait until the final node returned OK so that
	# each host down the line could then send OK back to the next
	# host etc.)
	t = threading.Thread(
		target = nextbounce,
		args = (
			request.json,
			random.choice(hosts)
		)
	)
	#start the thread
	t.start()
	#send the reply back to the previous host
	return 'ok'

# you will need to supply the port number you want this to run on as
# an argument.
if __name__ == "__main__":
	# start flask
	app.run(port=int(sys.argv[1]), host="0.0.0.0", debug=False)
