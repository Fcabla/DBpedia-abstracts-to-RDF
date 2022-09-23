import re
from typing import List

from spacy import Language, util
from spacy.tokens import Doc, Span
from transformers import pipeline


def extract_triplets(text: str) -> List[str]:
    """
    parses the text to triplets
    1. Split the text into tokens
    2. If the token is <triplet>, <subj>, or <obj>, then set the current variable to the appropriate value
    3. If the token is not one of the above, then append it to the appropriate variable
    4. If the current variable is <subj>, then append the triplet to the list of triplets

    :param text: str - the text to be parsed
    :type text: str
    :return: A list of dictionaries.
    """
    triplets = []
    relation, subject, relation, object_ = "", "", "", ""
    text = text.strip()
    current = "x"
    for token in text.replace("<s>", "").replace("<pad>", "").replace("</s>", "").split():
        if token == "<triplet>":
            current = "t"
            if relation != "":
                triplets.append(
                    {"head": subject.strip(), "type": relation.strip(), "tail": object_.strip()}
                )
                relation = ""
            subject = ""
        elif token == "<subj>":
            current = "s"
            if relation != "":
                triplets.append(
                    {"head": subject.strip(), "type": relation.strip(), "tail": object_.strip()}
                )
            object_ = ""
        elif token == "<obj>":
            current = "o"
            relation = ""
        else:
            if current == "t":
                subject += " " + token
            elif current == "s":
                object_ += " " + token
            elif current == "o":
                relation += " " + token
    if subject != "" and relation != "" and object_ != "":
        triplets.append(
            {"head": subject.strip(), "type": relation.strip(), "tail": object_.strip()}
        )

    return triplets


@Language.factory(
    "rebel",
    requires=["doc.sents"],
    assigns=["doc._.rel"],
    default_config={
        "model_name": "Babelscape/rebel-large",
        "device": 0,
    },
)
class RebelComponent:
    def __init__(
        self,
        nlp,
        name,
        model_name: str,
        device: int,
    ):
        assert model_name is not None, ""
        self.triplet_extractor = pipeline(
            "text2text-generation", model=model_name, tokenizer=model_name, device=device
        )
        # Register custom extension on the Doc
        if not Doc.has_extension("rel"):
            Doc.set_extension("rel", default={})

    def _generate_triplets(self, sents: List[Span]) -> List[List[dict]]:
        """
        1. We pass the text of the sentence to the triplet extractor.
        2. The triplet extractor returns a list of dictionaries.
        3. We extract the token ids from the dictionaries.
        4. We decode the token ids into text.
        5. We extract the triplets from the text.
        6. We return the triplets.

        The triplet extractor is a model that takes a sentence as input and returns a list of dictionaries.
        Each dictionary contains the token ids of the extracted triplets.

        The token ids are the numbers that represent the words in the sentence.
        For example, the token id of the word "the" is 2.

        The token ids are decoded into text using the tokenizer.
        The tokenizer is a model that takes a list of token ids as input and returns a list of words.

        :param sents: List[Span]
        :type sents: List[Span]
        :return: A list of lists of dicts.
        """
        output_ids = self.triplet_extractor(
            [sent.text for sent in sents], return_tensors=True, return_text=False
        )  # [0]["generated_token_ids"]
        extracted_texts = self.triplet_extractor.tokenizer.batch_decode(
            [out["generated_token_ids"] for out in output_ids]
        )
        extracted_triplets = []
        for text in extracted_texts:
            extracted_triplets.extend(extract_triplets(text))
        return extracted_triplets

    def set_annotations(self, doc: Doc, triplets: List[dict]):
        """
        The function takes a spacy Doc object and a list of triplets (dictionaries) as input.
        For each triplet, it finds the substring in the Doc object that matches the head and tail of the triplet.
        It then creates a spacy span object for each of the head and tail.
        Finally, it creates a dictionary of the relation type, head span and tail span and adds it to the Doc object

        :param doc: the spacy Doc object
        :type doc: Doc
        :param triplets: List[dict]
        :type triplets: List[dict]
        """
        for triplet in triplets:
            # get substring to spacy span
            head_span = re.search(triplet["head"], doc.text)
            tail_span = re.search(triplet["tail"], doc.text)
            # get spacy span
            if head_span is not None:
                head_span = doc.char_span(head_span.start(), head_span.end())
            else:
                head_span = triplet["head"]
            if tail_span is not None:
                tail_span = doc.char_span(tail_span.start(), tail_span.end())
            else:
                tail_span = triplet["tail"]
            offset = (head_span.start, tail_span.start)
            if offset not in doc._.rel:
                doc._.rel[offset] = {
                    "relation": triplet["type"],
                    "head_span": head_span,
                    "tail_span": tail_span,
                }

    def __call__(self, doc: Doc) -> Doc:
        """
        The function takes a doc object and returns a doc object

        :param doc: Doc
        :type doc: Doc
        :return: A Doc object with the sentence triplets added as annotations.
        """
        sentence_triplets = self._generate_triplets(doc.sents)
        self.set_annotations(doc, sentence_triplets)
        return doc

    def pipe(self, stream, batch_size=128):
        """
        It takes a stream of documents, and for each document,
        it generates a list of sentence triplets,
        and then sets the annotations for each sentence in the document

        :param stream: a generator of Doc objects
        :param batch_size: The number of documents to process at a time, defaults to 128 (optional)
        """
        for docs in util.minibatch(stream, size=batch_size):
            sents = []
            for doc in docs:
                sents += doc.sents
            sentence_triplets = self._generate_triplets(sents)
            index = 0
            for doc in docs:
                n_sent = len(list(doc.sents))
                self.set_annotations(doc, sentence_triplets[index : index + n_sent])
                index += n_sent
                yield doc
