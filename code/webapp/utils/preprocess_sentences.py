"""
Functions to extract and process the sentences from a DBpedia abstract
Author: Fernando Casabán Blasco and Pablo Hernández Carrascosa
"""
import re

######################
# Sentence functions #
######################


def get_sentences(doc):
    """
    Get a list with the sentences of the input document (spacy).
    """
    return list(doc.sents)


def clean_text(text):
    """
    Remove characters bounded by parentheses, always than there is no other parentheses inside.
    """
    text = re.sub(r"(\))(\")", r"\1 \2", text)
    text = re.sub("\([^()]+\) ", "", text)
    text = re.sub("\([^()]+\),", ",", text)
    text = re.sub("\([^()]+\).", ".", text)
    text = re.sub(r"(\.)([A-Za-z])", r"\1 \2", text)
    text = re.sub(r"(\;)([A-Za-z])", r"\1 \2", text)
    text = re.sub(r"(\")(\")", r"\1", text)
    return text
