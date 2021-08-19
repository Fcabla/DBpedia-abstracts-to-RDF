"""
Contains the first approach of extracting the clauses using ClausIE
Author: Fernando Casabán Blasco
"""

from pyclausie.Triples import Triple
import spacy
"""
#https://spacy.io/usage/linguistic-features#dependency-parse
#en_core_web_sm vs en_core_web_trf
"""
# Set a test text in order to test the algorythm
test_text = "Barack Hussein Obama II is an American politician who is the 44th and current President of the United States. He is the first African American to hold the office and the first president born outside the continental United States. Born in Honolulu, Hawaii, Obama is a graduate of Columbia University and Harvard Law School, where he was president of the Harvard Law Review. He was a community organizer in Chicago before earning his law degree. He worked as a civil rights attorney and taught constitutional law at the University of Chicago Law School between 1992 and 2004. While serving three terms representing the 13th District in the Illinois Senate from 1997 to 2004, he ran unsuccessfully in the Democratic primary for the United States Hou"

# Load model and parse text
nlp = spacy.load("en_core_web_sm")
doc = nlp(test_text)

# Extract the sentences
sentences = []
for sente in doc.sents:
    sentences.append(sente)
print("*"*150)

print("Ispect the first sentence")
for token in sentences[0]:
    print(token.text, token.dep_, token.head.text, token.head.pos_, [child for child in token.children])
    continue
print("*"*150)

print("Get unique types of dep_")
tps = []
for token in doc:
    tps.append(token.dep_)
print(set(tps))
print("*"*150)

# Extract triplets
print("Naive extraction of triplets")
def extract_subj_prd_obj(dep_tree_sent):
    # Multiple subj prd and obj can be found in a sentence
    subj = []
    pred = []
    obj = []

    tps = []
    for token in dep_tree_sent:
        tps.append(token.dep_)

    if 'nsubj' in tps: # nominal sentence
        nsubj_idxs = [index for index, value in enumerate(tps) if value == 'nsubj']
        prep_idxs = [index for index, value in enumerate(tps) if value == 'prep']
        
        if 'dobj' in tps:
            obj_idxs = [index for index, value in enumerate(tps) if value == 'dobj' or value == 'compound']

        elif 'pobj' in tps:
            obj_idxs = [index for index, value in enumerate(tps) if value == 'pobj' or value == 'compound']

        else:
            obj_idxs = [index for index, value in enumerate(tps) if value == 'xcomp' or value == 'compound']
        
        for idx in nsubj_idxs:
            subj.append(dep_tree_sent[idx])
        
        for idx in prep_idxs:
            pred.append(dep_tree_sent[idx])

        for idx in obj_idxs:
            obj.append(dep_tree_sent[idx])
        
    elif 'nsubjpass' in tps: # passive sentence
        pass
    
    return(subj, pred, obj)
subj, pred, obj = extract_subj_prd_obj(sentences[0])
print(subj, pred, obj)
print("*"*150)

print("Use noun chunks?")
for chunk in sentences[1].noun_chunks:
    print(chunk.text, chunk.root.text, chunk.root.dep_, chunk.root.head.text)
print("*"*150)


exit()
"""
from spacy.lang.en import English 

nlp = English()
nlp.add_pipe('sentencizer')


def split_in_sentences(text):
    doc = nlp(text)
    return [str(sent).strip() for sent in doc.sents]

print(split_in_sentences(test_text))
"""

"""
#import re
#sentences = re.split("\. ([A-Z])", test_text)
"""

"""
from nltk.tokenize import sent_tokenize

sentences = sent_tokenize(test_text)
print(sentences)
"""

"""
from pyclausie import ClausIE
cl = ClausIE.get_instance()
triples = cl.extract_triples([sentences[0]])
print(triples)
"""

"""


"""