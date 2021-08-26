"""
Functions to process the extracted triples from a set of sentences
Author: Fernando Casabán Blasco
"""

from spacy.symbols import nsubj, VERB, AUX, PUNCT
import spacy

##################
# Fixing triples #
##################
def fix_subj_complex_sentences(triples):
    """
    Function that takes the simplified sentences (with a clause modifier in the predicate) and substitutes the subject of the triple with
    the subject or object of the previous triple. This is because usually the simplified sentences has as subject terms like who, that, its, he.
    For example: 
    Original: Alchemy ...... that | was practiced | in China , India , the Muslim world , and Europe
    Results: Alchemy | was practiced | in China , India , the Muslim world , and Europe
    Returns a list of triples
    """
    new_triples = []
    for triple in triples:
        verbs = [tkn for tkn in triple.pred if tkn.pos == VERB]
        verbs = [verb for verb in verbs if (verb.dep_ in ["relcl", "acl", "advcl"] or verb.dep_ == "conj" and verb.head.pos == VERB)]
        previous_triple = []
        if verbs and (previous_triple or new_triples):
            new_triple = triple.get_copy()
            clausule_verb = verbs.pop()
            previous_triple = [t for t in new_triples if clausule_verb.head in t.get_all_tokens()]
            if not previous_triple:
                    previous_triple = new_triples[-1]
            else:
                previous_triple = previous_triple[-1]

            subject = [tkn for tkn in triple.subj if tkn.dep_.find("subj")]
            previous_subject = [tkn for tkn in previous_triple.subj if tkn.dep_.find("subj")]
            previous_object = [tkn for tkn in previous_triple.objct]
            if not subject or not previous_subject:
                new_triples.append(triple)
                continue
            else:
                subject = subject.pop()
                previous_subject = previous_subject.pop()
            
            chains = subject.doc._.coref_chains
            better_subj = chains.resolve(subject)
            if better_subj:
                # coreferee has found coreferences between the current and other triple, check if is the previous one
                if better_subj[0] in previous_triple.subj:
                    new_subj = previous_triple.subj.copy()
                    new_triple.subj = new_subj
                    new_triples.append(new_triple)
                elif better_subj[0] in previous_triple.objct:
                    new_subj = [tkn for tkn in clausule_verb.head.subtree if tkn in previous_triple.objct]
                    new_triple.subj = new_subj
                    new_triples.append(new_triple)
                else:
                    new_triples.append(get_subj_complex_sentence_helper(previous_triple, triple, clausule_verb, previous_subject, subject))
            else:
                new_triples.append(get_subj_complex_sentence_helper(previous_triple, triple, clausule_verb, previous_subject, subject))
        else:
            new_triples.append(triple)
    return new_triples

def get_subj_complex_sentence_helper(previous_triple, triple, clausule_verb, previous_subject, subject):
    """
    Function that takes the simplified sentences (with a clause modifier in the predicate) and substitutes the subject of the triple with
    the subject or object of the previous triple. This is because usually the simplified sentences has as subject terms like who, that, its, he.
    For example: 
    Original: Alchemy ...... that | was practiced | in China , India , the Muslim world , and Europe
    Results: Alchemy | was practiced | in China , India , the Muslim world , and Europe
    Returns a list of triples
    """
    result_triple = triple.get_copy()
    if clausule_verb.dep_ == "acl":
        new_subj = [tkn for tkn in previous_triple.objct]
        #result_triple = Triple(new_subj, triple.pred, triple.objct)
        result_triple.subj = new_subj
    elif clausule_verb.dep_ == "conj":
        new_subj = previous_triple.subj.copy()
        #result_triple = Triple(new_subj, triple.pred, triple.objct)
        result_triple.subj = new_subj
    else:
        if clausule_verb.dep_ == "advcl":
            #print(f"{triple} <> {previous_triple} <> {subject.dep_} <> {previous_subject.dep_}")
            pass
        #relcl, advcl
        if subject.dep_ == "nsubjpass" and previous_subject.dep_ == "nsubj":
            # take the subject of previous triplet as new subject
            new_subj = previous_triple.subj.copy()
            #result_triple = Triple(new_subj, triple.pred, triple.objct)
            result_triple.subj = new_subj
        elif subject.dep != previous_subject.dep:
            #subject.dep_ == "nsubj":
            #take the object of previous triplet as new subject
            new_subj = [tkn for tkn in clausule_verb.head.subtree if tkn in previous_triple.objct]
            #new_subj = [tkn for tkn in previous_triple.objct]
            if not new_subj:
                new_subj = [tkn for tkn in previous_triple.objct]
            #result_triple = Triple(new_subj, triple.pred, triple.objct)
            result_triple.subj = new_subj
        elif subject.dep_ == "nsubj" and previous_subject.dep_ == "nsubj":
            #subject.dep_ == "nsubjpass" or (
            # take the subject of previous triplet as new subject
            new_subj = previous_triple.subj.copy()
            #result_triple = Triple(new_subj, triple.pred, triple.objct)
            result_triple.subj = new_subj
        else:
            result_triple = triple

    return result_triple

def fix_aux_verbs(triples):
    """
    Appends more information to the predicate of the triples with just an auxiliary verb.
    Auxiliary verbs alone do not provide any information, here is an example:
    Original: He | is | a Professor at the Collège de France
    Result: He | is a Professor | at the Collège de France
    Returns a list of triples
    """
    new_triples = []
    for triple in triples:
        # Search triples with just one auxiliary verb
        if (len(triple.pred) == 1) and (triple.pred[0].pos == AUX):

            # retrieve all the tokens from the triple to identify possible candidates
            verb_subtree = [x for x in triple.pred[0].subtree]
            verb_subtree = [item for item in verb_subtree if item in triple.get_all_tokens()]
            verb_mod_explore = []
            for elem in verb_subtree:
                if(elem.dep_ == "attr" and elem.head.pos == AUX):
                    verb_mod_explore.append(elem)
                elif(elem.dep_ == "conj" and elem.head in verb_mod_explore ):
                    verb_mod_explore.append(elem)
            
            verb_mods = []
            for elem in verb_mod_explore:
                verb_mod = []
                explore_childs = [item for item in elem.children if item in triple.get_all_tokens()]
                for child in explore_childs:
                    if child.dep_ in ["det", "amod", "compound"]:
                        verb_mod.append(child)
                verb_mod.append(elem)
                verb_mods.append(verb_mod)

            # Build new object
            if verb_mods:
                if verb_mods[-1][-1] in triple.objct:
                    index = triple.objct.index(verb_mods[-1][-1])+1
                    new_obj = triple.objct[index:]

                    # Fix prepositions
                    if len(new_obj) > 0:
                        if new_obj[0].dep_ == "prep":
                            prep = new_obj.pop(0)
                            for v in verb_mods:
                                if(v[-1].dep_ != "prep"):
                                    v.append(prep)
                    
                    # Build new triples
                    for v in verb_mods:
                        new_triple = triple.get_copy()
                        new_triple.pred = new_triple.pred+v
                        new_triple.objct = new_obj
                        new_triples.append(new_triple)
            else:
                # short frase with no more information (it is in shape)
                new_triples.append(triple) 
        else:
            # If there is no single auxiliary verb append the triple to the new list of triples
            new_triples.append(triple)   
    
    return new_triples

def fix_xcomp_conj(triples):
    """
    Search for triples with a xcomp in the predicate and multiple conjunctions (verbs) in the object part and split them into multiple triples, for example:
    Original: Alchemists attempted to purify, mature, and perfect certain materials.
    Result: Alchemists | attempted to purify | certain materials, Alchemists | attempted to mature | certain materials, Alchemists | attempted to perfect | certain materials, 
    """
    new_triples = []
    for triple in triples:
        # any([tkn for tkn in triple.pred if tkn.dep_ == "xcomp"]) and 
        if any([tkn for tkn in triple.objct if tkn.dep_ == "conj" and (tkn.head.dep_ == "xcomp" and tkn.head in triple.pred)]):
            
            new_obj = triple.objct.copy()
            xcomp = [tkn for tkn in triple.pred if tkn.dep_ == "xcomp"].pop()
            xcomp_pred_idx = triple.pred.index(xcomp)
            conjunctions = [xcomp]
            # Search for conjunction tokens with xcomp or conj parents
            for token in triple.objct:
                if token.dep_ == "conj":
                    if token.head.dep_ in ["conj", "xcomp"]:
                        if token.pos == VERB or token.head in conjunctions:
                            conjunctions.append(token)
                            if token in new_obj:
                                new_obj.remove(token)

            # Remove remaining punct and cc related to conjunctions
            for conjunction in conjunctions:
                for child in conjunction.children:
                    if child.dep_ == "cc" or child.dep_ == "punct":
                        if child in new_obj:
                            new_obj.remove(child)

            # Build new triples
            for conjunction in conjunctions:
                new_triple = triple.get_copy()
                new_triple.pred[xcomp_pred_idx] = conjunction
                new_triple.objct = new_obj
                new_triples.append(new_triple)
        else:
            new_triples.append(triple)
    return new_triples

def append_preps_verbs(triples):
    """
    Search for prepositions in the object part of the triple and appends it to the predicate part of the triple, Here is an example:
    Original: He | was awarded | in 1982
    Result: He | was awarded in | 1982
    Returns a list of triples
    """
    new_triples=[]
    for triple in triples:
        verb = [tkn for tkn in triple.pred if tkn.pos_ == "VERB" or (tkn.pos_ == "AUX" and tkn.dep_ not in ["aux","auxpass"])]
        if verb:
            verb = verb.pop()
            prepositions = [tkn for tkn in verb.children if tkn.dep_ in ["prep","agent"]]
            if prepositions:
                for prep in prepositions:
                    if prep in triple.objct:
                        new_obj = [tkn for tkn in prep.subtree if tkn != prep]
                        new_triple = triple.get_copy()
                        new_triple.pred.append(prep)
                        new_triple.objct = new_obj
                        new_triples.append(new_triple)
            else:
                new_triples.append(triple)
    return new_triples

def split_conjunctions_subjs(triples):
    """
    Search for conjunctions in the subject of each triples and splits in new triples, here is an example:
    Original: Islamic and European alchemists | developed | a basic set of laboratory techniques , theories , and terms
    Result: Islamic alchemists | developed | a basic set of laboratory techniques , theories , and terms and 
    European alchemists | developed | a basic set of laboratory techniques , theories , and terms 
    Returns a list of triples
    """
    new_triples = []
    for triple in triples:
        conjunctions = [token for token in triple.subj if token.dep_ == "conj"]
        main_subject = [token for token in triple.subj if token.dep_.find("subj")]
        if main_subject:
            main_subject = main_subject.pop()
        else:
            # some error when finding the subj in the triple
            new_triples.append(triple)
            continue

        if conjunctions:
            #there is at least one conjunction.
            # First locate the token parent of the first conj and build the first subject
            subjects = []
            new_subject = []
            head_conj = conjunctions[0].head
            if head_conj.dep_ in ["compound", "amod", "nummod", "nmod", "advmod", "npadvmod"]:
                ancestors = [tkn for tkn in head_conj.ancestors]
                ancestors.insert(0,head_conj)
                if main_subject in ancestors:
                    subj_idx = ancestors.index(main_subject)+1
                    new_subject.extend(ancestors[:subj_idx])
                else:
                    continue
            else:
                # head_conj probably the subj
                new_subject.append(head_conj)
            subjects.append(new_subject)

            for conjunction in conjunctions:
                new_subject = []
                #if conjunction.head.dep_ == "amod":
                if conjunction.head.dep_ in ["compound", "amod", "nummod", "nmod", "advmod", "npadvmod"]:
                    # In case that the parent is amod, the child is also amod
                    # search the noun of the amod and build new triples
                    parent_mod = conjunction.head
                    new_subject.extend([conjunction,parent_mod.head])
                    #new_object.extend([parent_mod,parent_mod.head])
                    subjects.append(new_subject)

                else:
                    # parent is nsubj
                    for child in conjunction.children:
                        if child.dep_ in ["compound", "amod", "nummod", "nmod", "advmod", "npadvmod"]:
                            new_subject.append(child)
                    new_subject.append(conjunction)
                    subjects.append(new_subject)


            # Build triples
            for s in subjects:
                new_triple = triple.get_copy()
                new_triple.subj = s
                new_triples.append(new_triple)
        else:
            # There are no conjunctions, we store the triple without any operations
            new_triples.append(triple)
    return new_triples

def split_conjunctions_obj(triples):
    """
    Search for conjunctions in the object of each triples and splits in new triples, here is an example:
    Original: Alchemy | was practiced | in China , India , the Muslim world , and Europ
    Result: Alchemy | was practiced in | China , Alchemy | was practiced in | India ,
     Alchemy | was practiced in | the Muslim world , Alchemy | was practiced in | Europe
    Returns a list of triples
    """
    new_triples = []
    for triple in triples:
        conjunctions = [token for token in triple.objct if token.dep_ == "conj"]
        
        if conjunctions:
            #there is at least one conjunction.
            # First locate the token parent of the first conj and build the first object
            head_conj = conjunctions[0].head
            if head_conj in triple.objct:
                head_conj_idx = triple.objct.index(head_conj)
                main_part = triple.objct[:head_conj_idx]
                objects = []
                first_object = main_part.copy()
                # check if parent token (conj origin) have any modifier (compound or amod)
                if main_part:
                    if main_part[-1].dep_ in ["compound", "amod"] and head_conj.is_ancestor(main_part[-1]):
                        modifiers = [tkn for tkn in main_part[-1].subtree]
                        main_part = [elem for elem in main_part if elem not in modifiers]
                        first_object = main_part.copy()
                        first_object.extend(modifiers)

                first_object.append(head_conj)
                objects.append(first_object)

                for conjunction in conjunctions:
                    new_object = main_part.copy()
                    if conjunction.head.dep_ == "amod":
                        # In case that the parent is amod, the child is also amod
                        # search the noun of the amod and build new triples
                        # maybe check not the parent but the whole ancestors?
                        parent_mod = conjunction.head
                        new_object.extend([conjunction,parent_mod.head])
                        #new_object.extend([parent_mod,parent_mod.head])
                        objects.append(new_object)
                    else:
                        for child in conjunction.children:
                            if child.dep_ in ["amod", "compound"]:
                                new_object.append(child)
                        new_object.append(conjunction)
                        objects.append(new_object)

                # Build triples
                for o in objects:
                    new_triple = triple.get_copy()
                    new_triple.objct = o
                    new_triples.append(new_triple)
            else:
                # The conjunction parent is the verb or some other token outside the object part of the tripelt
                new_triples.append(triple)
        else:
            # There are no conjunctions, we store the triple without any operations
            new_triples.append(triple)
    return new_triples

def swap_subjects_correferences(triples, chains):
    """
    Description to do
    """
    new_triples = []
    for triple in triples:
        subj = triple.subj.copy()
        better_subj = None
        for token in subj:
            better_subj = chains.resolve(token)
            if better_subj:
                break
        if better_subj:
            better_subj = [tkn for tkn in better_subj[0].subtree]
            new_triple = triple.get_copy()
            new_triple.subj = better_subj
            new_triples.append(new_triple)
        else:
            # there arent correferences
            new_triples.append(triple)

    return new_triples