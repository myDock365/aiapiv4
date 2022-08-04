import string
from spacy.util import filter_spans
import spacy
from spacy.tokens import DocBin
from tqdm import tqdm
import dateutil.parser as dparser
from common.confidence_score_calculator import ConfidenceScore
from common.entities import *
from common.document import *
from spacy.matcher import Matcher
import re
from common.filter_entity import *
import spacy_transformers


class Trainer:
    entities_titles = [
        {"name": "ORG", "title": "Party"},
        {"name": "Address", "title": "Address Line 1"},
        {"name": "DATE", "title": "Effective Date"},
        {"name": "DATE", "title": "Expire Date"},
        {"name": "City", "title": "City"},
        {"name": "State", "title": "State"},
        {"name": "Country", "title": "Country"},
        {"name": "Zipcode", "title": "Zipcode"}
    ]

    entity_mapping = {
        "PARTY": "Party",
        "PARTIES": "Party",
        "ADDRESS": "Party Address 1",
        "EFFECTIVE DATE": "Effective Date",
        "GOVERNING LAW": "Governing Law",
        "PARTY ADDRESS": "Party Address 1",
        "AGREEMENT DATE": "Effective Date"
    }

    def __init__(self):
        self.entity_mapping = {
            "PARTY": "Party",
            "ADDRESS": "Party Address 1",
            "EFFECTIVE DATE": "Effective Date",
            "GOVERNING LAW": "Governing Law",
            "PARTY ADDRESS": "Party Address 1",
            "AGREEMENT DATE": "Effective Date"
        }

        self.rule = [{
            "entype": "Insurance",
            "entityValue": "Insurance,insurance"
        }, {
            "entype": "Warranty",
            "entityValue": "warranty,Warranty"
        },
            {
                "entype": "Termination",
                "entityValue": "terminate,terminated,Termination,termination"
            }
        ]

        self.governing_pattern = [{
            "name": "Governing Law",
            "pattern": [{'LEMMA': 'govern'},
                        {'IS_ALPHA': True, 'OP': '+'},
                        {"TEXT": ","},
                        {'IS_ALPHA': True, 'OP': '+'},
                        {'LEMMA': 'law'},
                        {'IS_ALPHA': True, 'OP': '+'},
                        {'ENT_TYPE': 'GPE'}
                        ]
        },{
            "name": "Governing Law",
            "pattern": [{'LEMMA': 'govern'},
                        {'IS_ALPHA': True, 'OP': '+'},
                        {'LEMMA': 'law'},
                        {'IS_ALPHA': True, 'OP': '+'},
                        {'ENT_TYPE': 'GPE'}
                        ]
        },
            {
                "name": "Governing Law",
                "pattern": [{'LEMMA': 'govern'},
                            {'IS_ALPHA': True, 'OP': '+'},
                            {"TEXT": ","},
                            {'IS_ALPHA': True, 'OP': '+'},
                            {"TEXT": ","},
                            {'IS_ALPHA': True, 'OP': '+'},
                            {'LEMMA': 'law'},
                            {'IS_ALPHA': True, 'OP': '+'},
                            {'ENT_TYPE': 'GPE'}
                            ]
            },
            {
                "name": "Governing Law",
                "pattern": [{'LEMMA': 'govern'},
                            {'IS_ALPHA': True, 'OP': '+'},
                            {"TEXT": ","},
                            {'IS_ALPHA': True, 'OP': '+'},
                            {"TEXT": ","},
                            {'IS_ALPHA': True, 'OP': '+'},
                            {'LEMMA': 'law'},
                            {'IS_ALPHA': True, 'OP': '+'},
                            {"TEXT": ","},
                            {'IS_ALPHA': True, 'OP': '+'},
                            {'ENT_TYPE': 'GPE'}
                            ]
            },
            {
                "name": "Governing Law",
                "pattern": [{'LEMMA': 'govern'},
                            {'IS_ALPHA': True, 'OP': '+'},
                            {"TEXT": ","},
                            {'IS_ALPHA': True, 'OP': '+'},
                            {'LEMMA': 'law'},
                            {'IS_ALPHA': True, 'OP': '+'},
                            {"TEXT": ","},
                            {'IS_ALPHA': True, 'OP': '+'},
                            {'ENT_TYPE': 'GPE'}
                            ]
            }

        ]

        self.pattern = [{
            "name": "Governing Law pattern 1",
            "pattern": [{'IS_ALPHA': True, 'OP': '+'},
                        {'LEMMA': 'govern'},
                        {'IS_ALPHA': True, 'OP': '+'},
                        {'LEMMA': 'law'},
                        {'IS_ALPHA': True, 'OP': '+'},
                        {'IS_ALPHA': True, 'OP': '+'},
                        {'TAG': '.'}]
        }, {
            "name": "Governing Law pattern 2",
            "pattern": [{'IS_ALPHA': True, 'OP': '+'},
                        {'LEMMA': 'govern'},
                        {'IS_ALPHA': True, 'OP': '+'},
                        {'LEMMA': 'law'},
                        {'IS_ALPHA': True, 'OP': '+'},
                        {'IS_PUNCT': True, 'OP': '+'},
                        {'IS_ALPHA': True, 'OP': '+'}
                        ]
        }, {
            "name": "Governing Law pattern 3",
            "pattern": [{'IS_ALPHA': True, 'OP': '+'},
                        {'LEMMA': 'govern'},
                        {'IS_ALPHA': True, 'OP': '+'},
                        {'LEMMA': 'law'},
                        {'IS_ALPHA': True, 'OP': '+'},
                        {'IS_ALPHA': True, 'OP': '+'}
                        ]
        }, {
            "name": "Insurance pattern 1",
            "pattern": [{'IS_ALPHA': True, 'OP': '+'},
                        {'LEMMA': 'insurance'},
                        {'IS_ALPHA': True, 'OP': '+'},
                        {'IS_ALPHA': True, 'OP': '+'},
                        {'IS_ALPHA': True, 'OP': '+'}
                        ]
        }, {
            "name": "Insurance pattern 2",
            "pattern": [{'IS_ALPHA': True, 'OP': '+'},
                        {'LEMMA': 'insurance'},
                        {'IS_ALPHA': True, 'OP': '+'},
                        {'IS_ALPHA': True, 'OP': '+'},
                        {'IS_ALPHA': True, 'OP': '+'},
                        {'TAG': '.'}
                        ]
        }, {
            "name": "Termination pattern 1",
            "pattern": [{'IS_ALPHA': True, 'OP': '+'},
                        {'LEMMA': 'termination'},
                        {'IS_ALPHA': True, 'OP': '+'},
                        {'IS_ALPHA': True, 'OP': '+'},
                        {'IS_PUNCT': True, 'OP': '+'},
                        {'IS_ALPHA': True, 'OP': '+'},
                        {'TAG': '.'}
                        ]
        }, {
            "name": "Termination pattern 2",
            "pattern": [{'IS_ALPHA': True, 'OP': '+'},
                        {'LEMMA': 'termination'},
                        {'IS_ALPHA': True, 'OP': '+'},
                        {'IS_ALPHA': True, 'OP': '+'},
                        {'IS_ALPHA': True, 'OP': '+'}
                        ]
        }, {
            "name": "Force Majure pattern 1",
            "pattern": [{'IS_ALPHA': True, 'OP': '+'},
                        {'LEMMA': 'force'},
                        {'IS_ALPHA': True, 'OP': '+'},
                        {'IS_ALPHA': True, 'OP': '+'},
                        {'IS_PUNCT': True, 'OP': '+'},
                        {'IS_ALPHA': True, 'OP': '+'},
                        {'TAG': '.'}
                        ]
        }, {
            "name": "Force Majure pattern 2",
            "pattern": [{'IS_ALPHA': True, 'OP': '+'},
                        {'LEMMA': 'force'},
                        {'IS_ALPHA': True, 'OP': '+'},
                        {'IS_ALPHA': True, 'OP': '+'},
                        {'IS_ALPHA': True, 'OP': '+'}
                        ]
        }]

    @staticmethod
    def convert_result(result, model):
        filtered_entities = []
        confidence_score_calculator: ConfidenceScore = ConfidenceScore()

        if len(result) > 0:
            for entity in result:
                entity_name = Trainer.entity_mapping.get(entity.label_)
                if entity_name:
                    entity_name = entity_name
                else:
                    entity_name = entity.label_

                score = 0.99

                if "date" in entity_name.lower():
                    score = confidence_score_calculator.find_confidence_Score(entity_name,
                                                                              entity.text,
                                                                              entity.start_char,
                                                                              result,
                                                                              2)
                elif "address" in entity_name.lower():
                    score = confidence_score_calculator.find_confidence_Score(entity_name,
                                                                              entity.text,
                                                                              entity.start_char,
                                                                              result,
                                                                              1)
                elif "organization" or "org" in entity_name.lower() or \
                        "company" in entity_name.lower():
                    score = confidence_score_calculator.find_confidence_Score(entity_name,
                                                                              entity.text,
                                                                              entity.start_char,
                                                                              result,
                                                                              3)
                elif "contact" in entity_name.lower() or \
                        "name" in entity_name.lower():
                    score = confidence_score_calculator.find_confidence_Score(entity_name,
                                                                              entity.text,
                                                                              entity.start_char,
                                                                              result,
                                                                              4)
                else:
                    score = confidence_score_calculator.find_confidence_Score(entity_name,
                                                                              entity.text,
                                                                              entity.start_char,
                                                                              result,
                                                                              7)

                entity_cleaned = Trainer.clean_entity_value(entity.text)

                ent = Entities(entity_name, entity_cleaned, model, entity.start_char,
                               entity.end_char - entity.start_char, score)
                filtered_entities.append(ent.toJSON())

        return filtered_entities

    @staticmethod
    def convert_to_doc(document_id, entities):
        ent = Document(document_id, entities)

        return ent.toJSON()

    def find_missing_entities(self, document, entities_found):

        result = self.is_all_found(entities_found)
        entities_unified = []

        for entity in entities_found:
            value = ""
            if entity.get("category") == "Party":
                value = FilterEntity.filter_party(entity.get("category"), entity.get("text"), entities_found)
            elif "governing" in entity.get("category"):
                pass
            elif "Address" in entity.get("category"):
                value = FilterEntity.filter_Adress(entity.get("category"), entity.get("text"), entities_found)
                address = Entities("Full Address",
                                   entity.get("text"),
                                   entity.get("model"),
                                   entity.get("offset"),
                                   entity.get("length"),
                                   entity.get("confidenceScore")
                                   )

                ent = Entities(entity.get("category"),
                               value.get("address_line_1"),
                               entity.get("model"),
                               entity.get("offset"),
                               entity.get("length"),
                               entity.get("confidenceScore")
                               )

                ent1 = Entities("City",
                                value.get("city"),
                                entity.get("model"),
                                entity.get("offset"),
                                entity.get("length"),
                                entity.get("confidenceScore")
                                )
                ent2 = Entities("State",
                                value.get("state"),
                                entity.get("model"),
                                entity.get("offset"),
                                entity.get("length"),
                                entity.get("confidenceScore")
                                )
                ent3 = Entities("Country",
                                value.get("country"),
                                entity.get("model"),
                                entity.get("offset"),
                                entity.get("length"),
                                entity.get("confidenceScore")
                                )

                ent4 = Entities("Zipcode",
                                value.get("zipcode"),
                                entity.get("model"),
                                entity.get("offset"),
                                entity.get("length"),
                                entity.get("confidenceScore")
                                )

                entities_unified.append(address.toJSON())
                entities_unified.append(ent.toJSON())
                entities_unified.append(ent1.toJSON())
                entities_unified.append(ent2.toJSON())
                entities_unified.append(ent3.toJSON())
                entities_unified.append(ent4.toJSON())
            else:
                value = entity.get("text")

            if "Address" not in entity.get("category"):
                ent = Entities(entity.get("category"),
                               value,
                               entity.get("model"),
                               entity.get("offset"),
                               entity.get("length"),
                               entity.get("confidenceScore")
                               )
                entities_unified.append(ent.toJSON())

        is_exist = result[0]
        missing_entities = result[1]

        governing_entity = self.perform_governing_law_rule(document)

        if governing_entity is not None:
            entities_unified.append(governing_entity.toJSON())

        if not is_exist:
            nlp = spacy.load("en_core_web_sm")
            entities = nlp(document)
            converted_result = self.convert_result(entities.ents, "new")

            for item in missing_entities:
                filtered = list(filter(lambda x: x.get("category") == item.get("name")
                                                 and float(x.get("confidenceScore")) > 0.85,
                                       converted_result))

                for filtered_entity in filtered:
                    ent = Entities(item.get("title"),
                                   filtered_entity.get("text"),
                                   "Default",
                                   filtered_entity.get("offset"),
                                   filtered_entity.get("length"),
                                   filtered_entity.get("confidenceScore")
                                   )
                    entities_unified.append(ent.toJSON())

        return entities_unified

    def is_all_found(self, entities_found):
        flag = True
        missing_entites = []

        for entity in self.entities_titles:
            filtered = list(filter(lambda x: x.get("category") == entity.get("title"), entities_found))

            if len(filtered) == 0:
                flag = False
                missing_entites.append(entity)

        return flag, missing_entites

    @staticmethod
    def clean_entity_value(entity):
        entity_cleaned = (re.sub(r'[_+!@#$?^.]+$', '', entity))
        entity_cleaned = (re.sub(r'[/\s+/g]+$', '', entity_cleaned))
        entity_cleaned = entity_cleaned.replace('\r\n', '')
        entity_cleaned = entity_cleaned.replace('\n', '')
        entity_cleaned = ' '.join(entity_cleaned.split())
        return entity_cleaned

    @staticmethod
    def clean_text_value(text):
        #text_cleaned = re.sub(r'[_+!@#$?^.]+$', '', text)
        #text_cleaned = re.sub(r'[/\s+/g]+$', '', text)
        text_cleaned = text.replace('\r\n', '')
        text_cleaned = text_cleaned.replace('\n', '')
        text_cleaned = ' '.join(text_cleaned.split())
        return text_cleaned

    def perform_governing_law_rule(self, document):
        nlp = spacy.load('en_core_web_sm')
        chars = re.escape(string.punctuation)
        # plaintext = re.sub(r'['+chars+']', '', document)
        plaintext = document #"Governing Law. This Agreement shall be governed by, and construed in accordance with, the laws of the State of Ohio applicable to contracts executed in and to be performed entirely within that state, without reference to conflicts of laws provisions."

        m_tool = Matcher(nlp.vocab)

        result = None

        for rule in self.governing_pattern:
            pattern = rule["pattern"]
            m_tool.add('QBF', [pattern])
            doc = nlp(plaintext)
            phrase_matches = m_tool(doc)
            print(phrase_matches)

            if len(phrase_matches) > 0:
                for match_id, start, end in phrase_matches:
                    string_id = nlp.vocab.strings[match_id]
                    span = doc[start:end]

                    if result is None:
                        result = Entities(rule.get("name"),
                                          span.text,
                                          "Default",
                                          start,
                                          end - start,
                                          1
                                          )

        return result

    def find_rule_result(self, document):
        # Load a pipeline and create the nlp object
        nlp = spacy.load("en_core_web_sm")
        filtered_entities = []
        # Initialize the matcher with the shared vocab

        for pat in self.pattern:
            # Add the pattern to the matcher
            matcher = Matcher(nlp.vocab)
            pattern = pat["pattern"]
            matcher.add("PATTERN", [pattern])

            # Process some text
            doc = nlp(document)

            # Call the matcher on the doc
            matches = matcher(doc)

            # for item in matches:
            # print("")

            # Iterate over the matches
            if len(matches) > 0:
                sorted_match = sorted(matches, key=lambda x: x[2] - x[1], reverse=True)[:1]
                for match_id, start, end in sorted_match:
                    # Get the matched span
                    matched_span = doc[start:end]
                    ent = Entities(pat["name"], matched_span.text, "From Rule", start, end - start)
                    filtered_entities.append(ent.toJSON())

        return filtered_entities

    def find_additionalEntities(self, paragraphs):
        filtered_entities = []
        for paragraph in paragraphs:
            for key in self.rule:
                for entity in key["entityValue"].split(","):
                    if entity in paragraph[1]:
                        ent = Entities(key["entype"], paragraph, 10, 10)
                        filtered_entities.append(ent.toJSON())

        return filtered_entities

    @staticmethod
    def sort_entities(entities):
        try:
            sorted_entities = sorted(entities, key=lambda x: x["confidenceScore"], reverse=True)
            return sorted_entities

        except None:
            return []

    @staticmethod
    def extract_entities(document, model):
        try:
            nlp_ner = spacy.load(model)
            doc = nlp_ner(document)
            return doc
        except Exception as e:
            return e

    @staticmethod
    def convert_training_data(training_data):
        nlp = spacy.blank("en")
        doc_bin = DocBin()
        for training_example in tqdm(training_data['annotations']):
            text = training_example['text']
            labels = training_example['entities']
            doc = nlp.make_doc(text)
            ents = []
            for start, end, label in labels:
                span = doc.char_span(start, end, label=label, alignment_mode="contract")
                if span is None:
                    print("Skipping entity")
                else:
                    ents.append(span)
            filtered_ents = filter_spans(ents)
            doc.ents = filtered_ents
            doc_bin.add(doc)

        doc_bin.to_disk("training_data.spacy")  # save the docbin object

    @staticmethod
    def get_paragraphs(text):
        en = spacy.load('en_core_web_sm')
        doc = en(text)

        seen = set()  # keep track of covered words

        chunks = []
        for sent in doc.sents:
            heads = [cc for cc in sent.root.children if cc.dep_ == 'conj']

            for head in heads:
                words = [ww for ww in head.subtree]
                for word in words:
                    seen.add(word)
                chunk = (' '.join([ww.text for ww in words]))
                chunks.append((head.i, chunk))

            unseen = [ww for ww in sent if ww not in seen]
            chunk = ' '.join([ww.text for ww in unseen])
            chunks.append((sent.root.i, chunk))

        chunks = sorted(chunks, key=lambda x: x[0])

        return chunks
