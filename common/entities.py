import json


class Entities:
    def __init__(self, entity_name, entity_value, model_name, start, length, score):
        self.entity_name = entity_name
        self.entity_value = entity_value
        self.model_name = model_name
        self.start = start
        self.length = length
        self.score = score

    def toJSON(self):
        return {
            "category": self.entity_name,
            "text": self.entity_value,
            "model": self.model_name,
            "offset": self.start,
            "length": self.length,
            "confidenceScore": self.score
        }
