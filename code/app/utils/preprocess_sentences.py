"""
Functions to extract and process the sentences from a DBpedia abstract
Author: Fernando Casabán Blasco
"""
import re
from spacy.symbols import nsubj, VERB, AUX, PUNCT
import spacy

######################
# Sentence functions #
######################

def get_sentences(doc):
    """
    Get a list with the sentences of the input document (spacy).
    """
    sentences = []
    for sente in doc.sents:
        sentences.append(sente)
    return(sentences)

def clean_text(text):
    #remove all the parentheses
    text = re.sub("\([^()]+\) ", "", text)
    # text = re.sub("\([^()]+\)", "", text, 1)
    return(text)

def get_dates_first_sentence(sentence):
    # month, day, year
    date_pattern1 = "(January|Jan|February|Feb|March|Mar|April|Apr|May|May|June|Jun|July|Jul|August|Aug|September|Sep|October|Oct|November|Nov|December|Dec) (\d{1,2}), (\d{4})"
    # day, month, year
    date_pattern2 = "(\d{1,2}) (January|Jan|February|Feb|March|Mar|April|Apr|May|May|June|Jun|July|Jul|August|Aug|September|Sep|October|Oct|November|Nov|December|Dec) (\d{4})"
    first_date = ""
    last_date = ""
    sentence = str(sentence)
    parnth = re.findall("\(.*?\)", sentence)
    if parnth:
        dp1 = re.findall(date_pattern1, sentence)
        dp2 = re.findall(date_pattern2, sentence)
        if dp1:
            if len(dp1) == 1:
                first_date = dp1[0][1] + " " + dp1[0][0] + " " + dp1[0][2]
            elif len(dp1) == 2:
                first_date = dp1[0][1] + " " + dp1[0][0] + " " + dp1[0][2]
                last_date = dp1[1][1] + " " + dp1[1][0] + " " + dp1[1][2]
        elif dp2:
            if len(dp2) == 1:
                first_date = dp2[0][0] + " " + dp2[0][1] + " " + dp2[0][2]
            elif len(dp2) == 2:
                first_date = dp2[0][0] + " " + dp2[0][1] + " " + dp2[0][2]
                last_date = dp2[1][0] + " " + dp2[1][1] + " " + dp2[1][2]

    return first_date, last_date

def get_dates_triples(sentence):
    results = []
    first_date, last_date = get_dates_first_sentence(sentence)
    if first_date:
        #results.append(f"individual born {first_date}")
        results.append(f"individual born {first_date}")
    if last_date:
        #results.append(f"individual death {last_date}")
        results.append(f"individual death {last_date}")
    return results

def get_sentences_by_nverbs(sentences):
    """
    Classifies each sentence from the input list of sentences into simple sentences or complex sentences.
    Simple sentences are those who sentences with just one verb (regular or auxiliary) or 2 verbs (aux + verb)
    Complex sentences are those with multiple verbs in one sentence, usually being clause modifiers
    """
    #sentences = get_sentences(doc)
    simple_sentences = []
    complex_sentences = []
    for s in sentences:
        regular_verbs = 0
        aux_verbs = 0
        mult_verbs = 0
        # Counting verbs
        for token in s:
            if(token.pos == VERB):
                regular_verbs = regular_verbs + 1
            elif(token.pos == AUX):
                aux_verbs = aux_verbs + 1
                if(token.head.pos == VERB):
                    mult_verbs = mult_verbs + 1

        # Classifying verbs into simple or complex sentences
        if(regular_verbs + aux_verbs == 1):
            simple_sentences.append(s)
        elif(regular_verbs == 1 and aux_verbs == 1):
            if(mult_verbs == 1):
                simple_sentences.append(s)
            else:
                complex_sentences.append(s)
        else:
            complex_sentences.append(s)
            
    return simple_sentences, complex_sentences

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


def simplify_sentence(complex_sentence):
    """
    Takes a complex sentence as imput and produce a list of simpler sentences of type span.
    The complex sentence is break down into simpler ones by lookin at certain dependency tags in the tokens, 
    these are clausual modifiers or complements.
    """
    # advcl: adverbial clause modifier
    # relcl: relative clause modifier
    # xcomp: open clausal complement 
    # acl: clausal modifier of noun (adjectival clause)
    # ccomp: clausal complement 
    # conj
    result_sentences = [] 
    root_clau = []
    clauses = []
    err = False
    for token in complex_sentence:
        if token.dep_ == "ROOT":
            root_clau.append(token)
        elif token.dep_ in  ["advcl", "relcl", "acl"]:
            clauses.append(token)
        elif token.dep_ == "conj" and token.head.pos == VERB:
            clauses.append(token)

    # Extract main simple sentence from complex sentence (only one root)
    for token in root_clau:
        sent = []
        for token_children in token.subtree:  
            ancestors = [t for t in token_children.ancestors]
            if any([t.dep_ in ["advcl", "acl", "relcl"] for t in ancestors]):
                break
            sent.append(token_children)
        # Make span
        try:
            result_sentences.append(sent[0].doc[sent[0].i : sent[-1].i+1])
        except:
            err = True
    if err:
        return []
    else:
        result_sentences.extend(get_simplified_sents_clauses(clauses))
        return result_sentences

def get_simplified_sents_clauses(clauses):
    """
    Function that takes a list of tokens with a dependency tag of a clause modifier and computes the subtree for each token.
    Then substracts the tokens of other simpler sentences (since the subtree can capture more than one simple sentence)
    Returns a list of simple sentence of type span
    """
    sentences = []
    for token in clauses:
        subtree = [t for t in token.subtree]
        substract_tokens = []
        for t in subtree:
            if t.dep_ in ["advcl", "acl", "relcl"] and t != token:
                substract_tokens.append(t)
        
        for st in substract_tokens:
            substract_subtree = [t for t in st.subtree]
            subtree = [x for x in subtree if x not in substract_subtree]
        
        # Make span
        sentences.append(subtree[0].doc[subtree[0].i : subtree[-1].i+1])

    return sentences
