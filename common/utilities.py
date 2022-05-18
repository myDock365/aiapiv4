from spacy.util import filter_spans
import spacy
from spacy.tokens import DocBin
from tqdm import tqdm
from common.entities import *


class Trainer:

    @staticmethod
    def convert_result(result):
        filtered_entities = []
        for entity in result:
            ent = Entities(entity.label_, entity.text)
            filtered_entities.append(ent.toJSON())

        return filtered_entities

    @staticmethod
    def extract_entities(document, model):
        nlp_ner = spacy.load(model)
        doc = nlp_ner(document)
        return doc;

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
