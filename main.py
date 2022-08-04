import os

from flask import Flask, jsonify, request
import json
from common.utilities import Trainer
from common.extraction_job import *

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
        # json_data = request.data.replace('"', '\"')
        data = json.loads(request.data, strict=False)
        model = data["model"]
        document = data["doc"]
        document = Trainer.clean_text_value(document)

        input_array = []
        max_n = 10000000
        for index in range(0, len(document), max_n):
            input_array.append(document[index: index + max_n])
        filtered_entities = []
        documents = []

        trainer = Trainer()

        for doc in input_array:
            for mod in model:

                entities = trainer.extract_entities(doc, app.root_path+mod["model_path"])
                filtered_entities += Trainer.convert_result(entities.ents, mod["model_name"])
                filtered_entities = trainer.find_missing_entities(doc, filtered_entities)
                # paragraphs = Trainer.get_paragraphs(document)
                # filtered_entities += trainer.find_additionalEntities(paragraphs)

            #filtered_entities =
            filtered_entities = Trainer.sort_entities(filtered_entities)
            document_json = Trainer.convert_to_doc(1, filtered_entities)
            documents.append(document_json)

        task = Job(documents)

        # for doc in input_array:
            # filtered_entities += trainer.find_rule_result(doc)

        return jsonify(task.toJSON())
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
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)

