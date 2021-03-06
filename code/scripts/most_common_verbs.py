""" 
Script to extract the most common verbs, verbs + prepositions and complex phrasal verbs in a sample of DBpedia abstracts.
Author: Fernando Casabán Blasco
"""

import spacy
import pandas as pd
from spacy.symbols import nsubj, VERB, AUX, PUNCT
from collections import Counter, OrderedDict
import re
import json

INPUT_FILE = "datasets/long-abstracts-sample.csv"
OUTPUT_FILE = "results/stats/simple_sentences_common_verbs_prep.json"

def clean_text(text):
    #remove all the parentheses
    text = re.sub("\([^()]+\) ", "", text)
    # text = re.sub("\([^()]+\)", "", text, 1)
    return(text)

def get_sentences(doc):
    """
    Get a list with the sentences of the input document (spacy).
    """
    sentences = []
    for sente in doc.sents:
        sentences.append(sente)
    return(sentences)

def get_num_verbs(sentence):
    """
    Get the number of verbs in the input sentence. Precisely returns 1 if the sentence is simple and 2 if the sentence is complex.
    Simple sentences are those who sentences with just one verb (regular or auxiliary) or 2 verbs (aux + verb).
    Complex sentences are those with multiple verbs in one sentence, usually being clause modifiers.
    Similiar to get_sentences_by_nverbs.
    """
    regular_verbs = 0
    aux_verbs = 0
    mult_verbs = 0
    for token in sentence:
        # count verbs
        if(token.pos == VERB):
            regular_verbs = regular_verbs + 1
        elif(token.pos == AUX):
            aux_verbs = aux_verbs + 1
            if(token.head.pos == VERB):
                mult_verbs = mult_verbs + 1

    # 1 regular verb or aux verbs
    if(regular_verbs + aux_verbs == 1):
        return 1
    
    elif(regular_verbs == 1 and aux_verbs == 1):
        if(mult_verbs == 1):
            return 1
        else:
            return 2
    else:
        return 2

def get_lemmatized_verbs(sentence):
    """ Returns the lemma of the verbs in the sentence """

    verbs = []
    for token in sentence:
        if token.pos == VERB:
            verbs.append(token.lemma_)
        if token.pos == AUX:
            if token.head.pos != VERB or token.dep_ not in ["aux","auxpass"]:
                verbs.append(token.lemma_)
    return verbs

def get_lemmatized_verbs_prepositions(sentence):
    """ Returns the lemma of the verbs in the sentence """
    results = []
    verbs = []
    for token in sentence:
        if token.pos == VERB:
            verbs.append(token)
        if token.pos == AUX:
            if token.head.pos != VERB or token.dep_ not in ["aux","auxpass"]:
                verbs.append(token)
    
    for verb in verbs:
        children = [x for x in verb.children]
        prep_found = False
        for child in children:
            if child.dep_ == "prep":
                results.append(f"{verb.lemma_} {child.text}")
                prep_found = True
        if not prep_found:
            results.append(verb.lemma_)
    return results

def get_prepositions(sentence):
    preps = []
    for token in sentence:
        if token.dep_ == "prep" and token.head.pos in [AUX, VERB]:
            preps.append(token.text)
    return preps

def main():
    nlp = spacy.load("en_core_web_trf")
    df = pd.read_csv(INPUT_FILE)
    abstracts = df['abstract'].to_list()
    verbs = []
    for abstract in abstracts:
        abstract = clean_text(abstract)
        doc = nlp(abstract)
        sentences = get_sentences(doc)
        for sentence in sentences:
            if get_num_verbs(sentence) == 1:
                #verbs.extend(get_lemmatized_verbs(sentence))
                verbs.extend(get_lemmatized_verbs_prepositions(sentence))
                #verbs.extend(get_prepositions(sentence))
    verbs = [verb.lower() for verb in verbs]
    verb_counter = Counter(verbs)
    verb_counter = OrderedDict(verb_counter.most_common())
    print(verb_counter)

    # save the results
    save_file = open(OUTPUT_FILE, "w")
    json.dump(verb_counter, save_file, indent=4)
    save_file.close()

if __name__ == "__main__":
    main()
