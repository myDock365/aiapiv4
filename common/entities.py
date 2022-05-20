import json


class Entities:
    def __init__(self, entity_name, entity_value):
        self.entity_name = entity_name
        self.entity_value = entity_value

    def toJSON(self):
        return {
            "entity": self.entity_name,
            "value": self.entity_value
        }
