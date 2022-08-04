import dateutil.parser as dparser
import re

from common.filter_entity import FilterEntity


class ConfidenceScore:

    def __init__(self):
        self.switcher = {
            1: self.calculate_address_confidence,
            2: self.calculate_date_confidence,
            3: self.calculate_organization_confidence,
            4: self.calculate_person_confidence,
            5: self.calculate_country_confidence,
            6: self.calculate_state_confidence,
            7: self.default
        }

    def find_confidence_Score(self, entity_name, entity_value, offset, entity, entity_type):
        return self.switcher.get(entity_type)(entity_name, entity_value, offset, entity)

    @staticmethod
    def calculate_address_confidence(entity_title, address, offset, entity):

        score = 0

        if offset < 1000:
            score = 0.01

        value = FilterEntity.filter_Adress(entity_title, address, [])

        try:
            if value.get("city") != "" and value.get("state") != "" and value.get("country") != "":
                score = 0.98 + score
            elif 3 < len(str(address).split(" ")) < 7:
                score = 0.95 + score
            elif 3 < len(str(address).split(" ")) < 8:
                score = 0.92 + score
            elif 4 < len(str(address).split(" ")) < 9:
                score = 0.98 + score
            else:
                score = 0.80 + score
        except None:
            score = 0.60 + score

        better_entities = list(filter(lambda x: x.label_ == entity_title
                                                and float(x.start_char) < offset, entity))

        if len(better_entities) == 0:
            score = score + 0.01

        return score

    @staticmethod
    def calculate_date_confidence(entity_title, date, offset, entity):

        score = 0

        if offset < 1000:
            score = 0.01

        try:
            if dparser.parse(date, fuzzy=True) and 6 < len(date) < 18:
                score = 0.98 + score
            elif dparser.parse(date, fuzzy=True) and 17 < len(date) < 24:
                score = 0.96 + score
            elif dparser.parse(date, fuzzy=True) and len(date) < 6:
                score = 0.80 + score
            else:
                score = 0.90 + score
        except:
            score = 0.80 + score

        better_entities = list(filter(lambda x: x.label_ == entity_title
                                                and float(x.start_char) < offset, entity))

        if len(better_entities) == 0:
            score = score + 0.01

        return score

    @staticmethod
    def calculate_organization_confidence(entity_title, address, offset, entity):
        expression = r"\b[A-Za-z,]\w+(?:\.com?)?(?:[ -]+(?:&[ -]+)?[A-Z]\w+(?:\.com?)?){0,2}[,\s]+(?i:ltd|pllc|llc|inc|plc|co(?:rp)?|group|holding|gmbh|solutions|solution)\b"

        score = 0

        if offset < 1000:
            score = 0.01

        try:
            if len(str(address).split(" ")) == 0:
                score = 0
            elif bool(re.match(expression, str(address).upper())):
                score = 0.98 + score
            elif 1 < len(str(address).split(" ")) < 2 and "inc" in str(address).lower():
                score = 0.96 + score
            elif 1 < len(str(address).split(" ")) < 3 and "inc" in str(address).lower():
                score = 0.95 + score
            elif 1 < len(str(address).split(" ")) < 4 and "inc" in str(address).lower():
                score = 0.94 + score
            elif len(str(address).split(" ")) == 1:
                score = 0.93 + score
            elif len(str(address).split(" ")) < 3:
                score = 0.92 + score
            elif len(str(address).split(" ")) < 5:
                score = 0.60 + score
            else:
                score = 0.80 + score
        except:
            score = 0.60 + score

        better_entities = list(filter(lambda x: x.label_ == entity_title
                                                and float(x.start_char) < offset, entity))

        if len(better_entities) == 0:
            score = score + 0.01

        return score

    @staticmethod
    def calculate_country_confidence(entity_title, address, offset, entity):
        return 0.90

    @staticmethod
    def calculate_person_confidence(entity_title, address, offset, entity):
        return 0.90

    @staticmethod
    def calculate_state_confidence(entity_title, address, offset, entity):
        return 0.90

    @staticmethod
    def default(entity_title, address, offset, entity):
        return 1
