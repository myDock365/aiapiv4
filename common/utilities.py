from spacy.util import filter_spans
import spacy
from spacy.tokens import DocBin
from tqdm import tqdm
from common.entities import *
from spacy.matcher import Matcher


class Trainer:

    def __init__(self):
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
        for entity in result:
            ent = Entities(entity.label_, entity.text, model)
            filtered_entities.append(ent.toJSON())

        return filtered_entities

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

            #for item in matches:
                #print("")

            # Iterate over the matches
            if len(matches) > 0:
                sorted_match = sorted(matches, key=lambda x: x[2]-x[1], reverse=True)[:1]
                for match_id, start, end in sorted_match:
                    # Get the matched span
                    matched_span = doc[start:end]
                    ent = Entities(pat["name"], matched_span.text, "From Rule")
                    filtered_entities.append(ent.toJSON())

        return filtered_entities

    def find_additionalEntities(self, paragraphs):
        filtered_entities = []
        for paragraph in paragraphs:
            for key in self.rule:
                for entity in key["entityValue"].split(","):
                    if entity in paragraph[1]:
                        ent = Entities(key["entype"], paragraph)
                        filtered_entities.append(ent.toJSON())

        return filtered_entities

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
