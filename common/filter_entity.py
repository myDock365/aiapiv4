import re

import spacy
import locationtagger
from address_parser import Parser


class FilterEntity:

    @staticmethod
    def filter_party(entity_name, entity_value, all_entities):
        expression = r"\b[A-Z]\w+(?:\.com?)?(?:[ -]+(?:&[ -]+)?[A-Z]\w+(?:\.com?)?){0,2}[,\s]+(?i:ltd|llc|inc|plc|co(?:rp)?|group|holding|gmbh|solutions|solution)\b"

        entity_cleaned = ""

        if len(entity_value) > 30:
            if entity_name == "Party":
                ner = spacy.load("en_core_web_sm")
                entities = ner(entity_value)

                for company in entities.ents:
                    if company.label_ == "ORG"\
                            and (len(company.text) > 30
                                 or bool(re.fullmatch(expression, str(company.text).lower()))):
                        entity_cleaned = company.text

                return entity_cleaned

        return entity_value

    @staticmethod
    def filter_date(entity_name, entity_value, all_entities):
        if "date" in entity_name.lower():
            entity_cleaned = dparser.parse(entity_value, fuzzy=True)

    @staticmethod
    def filter_Adress(entity_name, entity_value, all_entities):

        flag = False

        city = ""
        state = ""
        country = ""
        zipcode = ""
        address_line_one = ""

        for entity in all_entities:

            value = entity.get("text")

            if entity.get("category") == "City":
                city = value
            elif entity.get("category") == "State":
                state = value
            elif entity.get("category") == "Country":
                country = value
            elif entity.get("category") == "Zipcode":
                zipcode = value

        if (city == "" or state == "" or country == "") and entity_value != "":
            location = locationtagger.find_locations(text=entity_value)

            if len(location.countries) > 0:
                country = location.countries[0]
            elif len(location.other_countries) > 0:
                country = location.other_countries[0]

            if len(location.regions) > 0:
                state = location.regions[0]
            elif len(location.other_regions) > 0:
                state = location.other_regions[0]

            if len(location.cities) > 0:
                city = location.cities[0]

        if zipcode == "":
            parser = Parser()
            adr = parser.parse(entity_value)

            if adr and adr.dict:
                zipcode = adr.dict.get("locality").get("zip")
                address_line_one = adr.street_str()

        return {
            "address_line_1": address_line_one,
            "city": city,
            "state": state,
            "country": country,
            "zipcode": zipcode
        }
