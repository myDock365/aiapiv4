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

