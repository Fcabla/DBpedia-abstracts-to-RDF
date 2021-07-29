def simplify_sentence_old(complex_sentence):
    # advcl: adverbial clause modifier
    # relcl: relative clause modifier
    # xcomp: open clausal complement 
    # acl: clausal modifier of noun (adjectival clause)
    # ccomp: clausal complement 
    # conj
    
    root_clau = []
    adv_clau = []
    rela_clau = []
    acl_clau = []
    conj_clau = []
    # xcomp = []
    for token in complex_sentence:
        if token.dep_ == "ROOT":
            print(token.text, token.dep_, token.pos_)
            root_clau.append(token)
        elif token.dep_ == "advcl":
            print(token.text, token.dep_)
            adv_clau.append(token)
        elif token.dep_ == "relcl":
            print(token.text, token.dep_)
            rela_clau.append(token)
        elif token.dep_ == "acl":
            print(token.text, token.dep_)
            acl_clau.append(token)
        if token.dep_ == "conj" and token.head.pos == VERB:
            print(token.text, token.dep_)
            conj_clau.append(token)

    # This should be put into a function to avoid code rep 
    # only one root 
    for token in root_clau:
        sent = []
        for token_children in token.subtree:            
            ancestors = [t for t in token_children.ancestors]
            if any([t.dep_ in ["advcl", "acl", "relcl"] for t in ancestors]):
                break
            sent.append(token_children)
        print(' '.join([t.text for t in sent]))
        print("----")

    get_simplified_sents(adv_clau)
    get_simplified_sents(rela_clau)
    get_simplified_sents(acl_clau)
    get_simplified_sents(conj_clau)

    
def get_simplified_sents_old(clausules_tokens):
    for token in clausules_tokens:
        sent = []
        for token_children in token.subtree:
            ancestors = [t for t in token_children.rights]
            sent.append(token_children.text)
            if any([t.dep_ in ["advcl", "acl", "relcl"] and t != token for t in ancestors]):
                print([t.dep_ in ["advcl", "acl", "relcl"] and t != token for t in ancestors])
                print(ancestors, token_children)
                if token_children.dep_ != "xcomp":
                    
                    break
        
        print(' '.join(sent))
        print("----")

def split_conjunctions_obj_old(triples):
    """
    Search for conjunctions in the object of each triples and splits in new triples, here is an example:
    Original: A, or a, | is | the first letter 
    Result: A | is | the first letter, a | is | the first letter 
    Returns a list of triples
    """
    new_triples = []
    
    for triple in triples:
        objs = []
        obj = []
        for token in triple.objct:
            if token.dep_ == "cc" or token.dep_ == "punct" :
                objs.append(obj)
                obj = []
            else:
                obj.append(token)

        if objs:
            for o in objs:
                new_triples.append(Triple(triple.subj,triple.pred,o))

        else:
            new_triples.append(triple)
    return new_triples

def split_conjunctions_subjs_old(triples):
    """
    Search for conjunctions in the subject of each triples and splits in new triples, here is an example:
    Original: A, or a, | is | the first letter 
    Result: A | is | the first letter, a | is | the first letter 
    Returns a list of triples
    """
    new_triples = []
    for triple in triples:
        for token in triple.subj:
            if token.dep_ == "conj":
                new_triples.append(Triple([token], triple.pred, triple.objct))
                triple.subj.remove(token)
            elif token.dep_ == "punct" or token.dep_ == "cc":
                triple.subj.remove(token)
        new_triples.append(triple)
    return new_triples