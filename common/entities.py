import json


class Entities:
    def __init__(self, entity_name, entity_value, model_name):
        self.entity_name = entity_name
        self.entity_value = entity_value
        self.model_name = model_name

    def toJSON(self):
        return {
            "entity": self.entity_name,
            "value": self.entity_value,
            "model": self.model_name
        }
