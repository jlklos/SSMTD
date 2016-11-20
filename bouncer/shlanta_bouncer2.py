from flask import Flask, abort, request
import requests
import random
import sys
import threading
app = Flask(__name__)

#either other remote bouncers or the endpoint
hosts = ['35.160.21.18:8888']

@app.route('/', methods=['POST'])
def bounce():
<<<<<<< HEAD
        def nextbounce(json):
                requests.post("http://%s"%random.choice(hosts), json=json)
                return
=======
	def nextbounce(json):
		requests.post("http://%s"%random.choice(hosts), json=json)
		return

	print "Got something"
	if not request.json:
		return abort(400)
	t= threading.Thread(target=nextbounce, args=(request.json, ))
	t.start()
	return 'ok'
>>>>>>> b30501d16416a54c8af96bde59742f2f679a4df7

        print "Got something"
        if not request.json:
                return abort(400)
        t= threading.Thread(target=nextbounce, args=(request.json, ))
        t.start()
        return 'ok'

#you will need to supply the port number you want this to run on as an $
if __name__ == "__main__":
<<<<<<< HEAD
        app.run(port=int(sys.argv[1]), host="0.0.0.0", debug=False)


=======
	app.run(port=int(sys.argv[1]), host="0.0.0.0", debug=False)
>>>>>>> b30501d16416a54c8af96bde59742f2f679a4df7
