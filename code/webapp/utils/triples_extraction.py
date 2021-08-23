"""
Functions to extract triples from a set of sentences
Author: Fernando Casabán Blasco
"""

import spacy
from utils.preprocess_sentences import get_num_verbs, simplify_sentence
from utils.process_triples import fix_subj_complex_sentences

class Triple:
    def __init__(self, subj, pred, objct, sent):
        """list of tokens"""
        self.subj = subj
        self.pred = pred
        self.objct = objct
        self.sent = sent

    def get_copy(self):
        return Triple(self.subj.copy(), self.pred.copy(), self.objct.copy(), self.sent)

    def get_all_tokens(self):
        """
        Returs a list with all the tokens in the triple
        """
        return self.subj + self.pred + self.objct

    def set_rdf_triples(self, subj, pred, objct):
        self.subj_rdf = subj
        self.pred_rdf = pred
        self.objct_rdf = objct

    def get_rdf_triple(self):
        return f"{self.subj_rdf} | {self.pred_rdf} | {self.objct_rdf}"

    def __repr__(self):
        return f"{' '.join([x.text for x in self.subj])} | {' '.join([x.text for x in self.pred])} | {' '.join([x.text for x in self.objct])}"

    def __str__(self):
        return f"{' '.join([x.text for x in self.subj])} {' '.join([x.text for x in self.pred])} {' '.join([x.text for x in self.objct])}"

    
################################
# Triples extraction functions #
################################

def get_simple_triples(sentence):
    """
    Get the triples from each sentence in <subject, predicate, object> format.
    Firs identify the root verb of the dependency tree and explore each subtrees.
    If a subtree contains any kind of subject, all the subtree will be classified as subject, 
    the same happens with the objects.
    This function only works with simple sentences.
    """
    triples = []
    subjs = []
    objs = []
    preds = []
    root_token = sentence.root
    preds.append(root_token)
    for children in root_token.children:
        if(children.dep_ in ["aux","auxpass"]):
            # children.pos == AUX
            #preds.insert(0,children)
            preds.append(children)
        elif(children.dep_ == "neg"):
            #negative
            #preds.insert(1,children)
            preds.append(children)
        elif(children.dep_ == "xcomp"):
            # consider the prepositions between both verbs (was thought to result)
            xcomp_lefts = [tkn for tkn in children.lefts]
            preds.extend(xcomp_lefts)
            preds.append(children)
        elif children.dep_.find("mod"):
            # advmod
            pass
            #preds.append(children)
        
        preds.sort(key=lambda token: token.i)
        # retrieve subtrees
        is_subj = False
        is_obj = False
        temp_elem = []
        for token_children in children.subtree:
            if token_children in sentence:
                if token_children.dep_.find("subj") == True:
                    is_subj = True
                elif token_children.dep_.find("obj") == True:
                    is_obj = True
                elif token_children.dep_ == "attr":
                    is_obj = True
                if token_children not in preds:
                    temp_elem.append(token_children)
        if is_subj:
            subjs.append(temp_elem)
        elif is_obj:
            objs.append(temp_elem)
    # Build triples
    for s in subjs:
        for o in objs:
            triples.append(Triple(s,preds.copy(),o, sentence))
    return triples

def get_all_triples(sentences, use_comp_sents=False):
    """ 
    Extract all the triples from the input list of sentences. Triples can be extracted from simple and complex senteces.
    Returns a list of objects of class Triple.
    """
    triples = []
    for sentence in sentences:
        # complex sentence
        if get_num_verbs(sentence) > 1:
            if use_comp_sents:
                simple_sentences = simplify_sentence(sentence)
                for sent in simple_sentences:
                    tps = get_simple_triples(sent)
                    triples.extend(tps)
        # simple sentence
        else:
            tps = get_simple_triples(sentence)
            triples.extend(tps)
    triples = fix_subj_complex_sentences(triples)
    return triples
