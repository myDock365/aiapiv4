import json


class Document:
    def __init__(self, did, entities):
        self.id = did
        self.entities = entities

    def toJSON(self):
        return {
            "id": self.id,
            "entities": self.entities
        }
