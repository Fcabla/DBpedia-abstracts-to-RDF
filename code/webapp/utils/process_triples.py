"""
Functions to process the extracted triples from a set of sentences
Author: Fernando Casabán Blasco and Pablo Hernández Carrascosa
"""
import utils.triples_extraction as te
from spacy.matcher import DependencyMatcher


##################
# Fixing triples #
##################


def split_amod_conjunctions_subj(nlp, triples):
    """
    Search for amod tokens in the subject of each triple (chained amod tokens) and splits in new triples, Example:
    Original: Islamic and European alchemists | developed | some theories
    Result: Islamic alchemists | developed | some theories, European alchemists | developed | some theories
    Returns the list of triples
    """
    new_triples = []
    for triple in triples:
        subject_text = ''.join(token.text_with_ws for token in triple.subj)

        doc = nlp(subject_text)

        patt_amod_conj = [{"RIGHT_ID": "propn", "RIGHT_ATTRS": {"DEP": "ROOT"}},
                          {"LEFT_ID": "propn", "REL_OP": ">", "RIGHT_ID": "adjetive", "RIGHT_ATTRS": {"DEP": "amod"}},
                          {"LEFT_ID": "adjetive", "REL_OP": ">", "RIGHT_ID": "conj", "RIGHT_ATTRS": {"DEP": "conj"}}]

        dep_matcher = DependencyMatcher(nlp.vocab)
        dep_matcher.add("patt_amod_conj", [patt_amod_conj])
        dep_matches = dep_matcher(doc)

        if not dep_matches:
            new_triples.append(triple)
            continue

        simpler_subjects = []
        # Iterate over the matches
        for match_id, token_id in dep_matches:
            string_id = nlp.vocab.strings[match_id]  # Get string representation
            if string_id == "patt_amod_conj":
                conjs = doc[token_id[1]].conjuncts  # coordinated "amod" tokens, not including the token itself
                shared_text_left = doc[:token_id[1]]  # span previous to the first amod
                shared_text_right = doc[(conjs[-1].i + 1):]  # span after last amod

                new = [token for token in shared_text_left]
                new.append(doc[token_id[1]])
                new.extend([token for token in shared_text_right])
                simpler_subjects.append(new)

                for c in conjs:
                    new = [token for token in shared_text_left]
                    new.append(c)
                    new.extend([token for token in shared_text_right])
                    simpler_subjects.append(new)

                # Build triples
                for s in simpler_subjects:
                    new_triple = triple.get_copy()
                    new_triple.subj = s
                    new_triples.append(new_triple)
    return new_triples


def split_amod_conjunctions_obj(nlp, triples):
    """
    Search for amod tokens in the object of each triple (chained amod tokens) and splits in new triples, Example:
    Original: Obama | is | the 44th and current President
    Result: Obama | is | the 44th President, Obama | is | the current President
    Returns the list of triples
    """
    new_triples = []
    for triple in triples:
        object_text = ''.join(token.text_with_ws for token in triple.objct)

        doc = nlp(object_text)

        patt_amod_conj = [{"RIGHT_ID": "root", "RIGHT_ATTRS": {"DEP": "ROOT"}},
                          {"LEFT_ID": "root", "REL_OP": ">", "RIGHT_ID": "adjetive", "RIGHT_ATTRS": {"DEP": "amod"}},
                          {"LEFT_ID": "adjetive", "REL_OP": ">", "RIGHT_ID": "conj", "RIGHT_ATTRS": {"DEP": "conj"}}]

        dep_matcher = DependencyMatcher(nlp.vocab)
        dep_matcher.add("patt_amod_conj", [patt_amod_conj])
        dep_matches = dep_matcher(doc)

        if not dep_matches:
            new_triples.append(triple)
            continue

        simpler_objects = []
        # Iterate over the matches
        for match_id, token_id in dep_matches:
            string_id = nlp.vocab.strings[match_id]  # Get string representation
            if string_id == "patt_amod_conj":
                conjs = doc[token_id[1]].conjuncts  # coordinated "amod" tokens, not including the token itself
                shared_text_left = doc[:token_id[1]]  # span previous to the first amod
                shared_text_right = doc[(conjs[-1].i + 1):]  # span after last amod

                new = [token for token in shared_text_left]
                new.append(doc[token_id[1]])
                new.extend([token for token in shared_text_right])
                simpler_objects.append(new)

                for c in conjs:
                    new = [token for token in shared_text_left]
                    new.append(c)
                    new.extend([token for token in shared_text_right])
                    simpler_objects.append(new)

            # Build triples
            for o in simpler_objects:
                new_triple = triple.get_copy()
                new_triple.objct = o
                new_triples.append(new_triple)
    return new_triples
