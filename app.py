import os

from flask import Flask, jsonify, request
import json
from common.utilities import Trainer

# creating a Flask app
app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello, World!"

# on the terminal type: curl http://127.0.0.1:5000/
# returns hello world when we use GET.
# returns the data that we send when we use POST.
@app.route('/extract', methods=['POST'])
def home():
    error = "First"
    try:
        data = json.loads(request.data)
        error = "second"
        model = data["model"]
        error = "second 1"
        document = data["doc"]
        error = "second 2"
        trainer = Trainer()
        error = "second 3"
        entities = trainer.extract_entities(document, app.root_path+model)
        error = entities
        filtered_entities = Trainer.convert_result(entities.ents)
        return jsonify(filtered_entities)
    except Exception as ex:
        return "Error"+ex


# A simple function to calculate the square of a number
# the number to be squared is sent in the URL when we use GET
# on the terminal type: curl http://127.0.0.1:5000 / home / 10
# this returns 100 (square of 10)
@app.route('/home/<int:num>', methods=['GET'])
def disp(num):
    return jsonify({'data': num ** 2})


# driver function
#if __name__ == '__main__':
    #app.run(port=5000)

