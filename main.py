from flask import Flask, jsonify, request
import json
from common.utilities import Trainer

# creating a Flask app
app = Flask(__name__)


# on the terminal type: curl http://127.0.0.1:5000/
# returns hello world when we use GET.
# returns the data that we send when we use POST.
@app.route('/', methods=['POST'])
def home():
    data = json.loads(request.data)
    model = data["model"]
    document = data["doc"]

    trainer = Trainer()
    entities = trainer.extract_entities(document, model)
    filtered_entities = Trainer.convert_result(entities.ents)
    return jsonify(filtered_entities)


# A simple function to calculate the square of a number
# the number to be squared is sent in the URL when we use GET
# on the terminal type: curl http://127.0.0.1:5000 / home / 10
# this returns 100 (square of 10)
@app.route('/home/<int:num>', methods=['GET'])
def disp(num):
    return jsonify({'data': num ** 2})


# driver function
if __name__ == '__main__':
    app.run(host="0,0,0,0", port=5000)

