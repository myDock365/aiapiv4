import json


class Entities:
    def __init__(self, entity_name, entity_value):
        self.entity_name = entity_name
        self.entity_value = entity_value

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)
