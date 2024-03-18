import logging
import datetime
from flask import Flask, request, jsonify
from back.generate import Payload, GeneratePower

logging.basicConfig(filename='./log/log_{}.log'.format(datetime.datetime.now()), 
	level=logging.ERROR,
	format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)

@app.route('/productionplan', methods=['POST'])
def handle_request():
    """
    This endpoint catches a json request and use it to choose powerplants that will produce power
    :return: A json response containing the choosen powerplants and how much power they will produce
    """
    payload = request.get_json()
    powerplants = Payload(payload).create_powerplants() # create the powerplants based on the received payload

    if powerplants: # if there is at least one powerplant available
    	result = GeneratePower(powerplants).export() ## generate power and export the results
    else:
    	message = "The payload is missing data"
    	result = {'error':message}
    	logging.error(message)

    return jsonify(result) # final results

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug="True", port=8888)