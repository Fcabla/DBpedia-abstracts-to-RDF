import pandas as pd
import requests
import json
from rdflib import Graph, OWL, RDFS, RDF, URIRef, Literal

SPOTLIGHT_LOCAL_URL = "http://localhost:2222/rest/annotate/"
SPOTLIGHT_ONLINE_API = "https://api.dbpedia-spotlight.org/en/annotate"
UNKOWN_VALUE = "UNK"
DEFAULT_VERB = "DEF"

###############
# Text to RDF #
###############

def get_annotated_text_dict(text, service_url=SPOTLIGHT_ONLINE_API, confidence=0.3, support=0, dbpedia_only = True):
    """
    Function that query's the dbpedia spotlight api with the document text as input. Confidence level is the
    confidence score for disambiguation / linking and support is how prominent is this entity in Lucene Model, i.e. number of inlinks in Wikipedia.
    Returns a dictionary with term-URI and a dictionary with term-types (from an ontology)
    """
    headerinfo = {'Accept': 'application/json'}
    parameters = {'text': text, 'confidence': confidence, 'support': support}
    term_URI_dict = {}
    term_types_dict = {}
    try:
        if "localhost" in service_url:
            resp = requests.post(service_url, data=parameters, headers=headerinfo)
        else:
            resp = requests.get(service_url, params=parameters, headers=headerinfo)
    except:
        try:
            print("Error at dbpedia spotlight post/get, trying with the api one")
            service_url = SPOTLIGHT_ONLINE_API
            resp = requests.get(service_url, params=parameters, headers=headerinfo)
        except:
            print("Error at dbpedia spotlight post/get")
            return None

    if resp.status_code != 200:
        print(f"error, status code{resp.status_code}")
        return None
    else:
        
        decoded = json.loads(resp.text)

        if 'Resources' in decoded:
            for dec in decoded['Resources']:
                term_URI_dict[dec['@surfaceForm'].lower()] = dec['@URI'].lower()
                term_types_dict[dec['@URI'].lower()] = dec['@types'].lower().split(",")

            if dbpedia_only:
                for key,value in term_types_dict.items():
                    value = [x.replace('dbpedia:', 'https://dbpedia.org/ontology/') for x in value if "dbpedia:" in x]
                    term_types_dict[key] = value

    return term_URI_dict, term_types_dict

def load_dbo_graph(dbo_path):
    """ Return the ontology as a rdflib graph """
    try:
        g = Graph()
        g.parse(dbo_path)
    except:
        print(f"Error while parsing the {dbo_path} file (dbpedia ontology file), please check if the file is in a recheable folder and if the path is correct")
        exit()
    return g

def load_lexicalization_table(lex_path):
    """ Return the lexicalization table as a python dict of dics (verbs and prepositions, classes) """
    try:
        with open(lex_path) as json_file:
            lexicalization_table = json.load(json_file)
    except:
        print(f"Error while parsing the {lex_path} file, please check if the file is in a recheable folder and if the path is correct")
        exit()
    return lexicalization_table

def replace_text_URI(triples, term_URI_dict, term_types_dict, prop_lex_table, cla_lex_table, dbo_graph):
    """
    Maybe this function should be inside the triple class
    """
    new_triples = []
    for triple in triples:
        subj = [x for x in triple.subj if x.dep_ != "det"]
        subj = ' '.join([x.text.lower() for x in subj])
        orginal_pred = ' '.join([x.text.lower() for x in triple.pred])
        objct = ' '.join([x.text.lower() for x in triple.objct])
        
        verb = [tkn for tkn in triple.pred if tkn.pos_ == "VERB" or (tkn.pos_ == "AUX" and tkn.dep_ not in ["aux","auxpass"])].pop()
        verb = str(verb.lemma_)
        prep = [tkn.text for tkn in triple.pred if tkn.dep_ == "prep"]
        if prep:
            prep = prep.pop()
            prep = prep.lower()
        else:
            prep = DEFAULT_VERB

        # NER the subject
        s_candidates = []
        keys = []
        for key in term_URI_dict.keys():
            if key in subj.lower():
                s_candidates.append(term_URI_dict[key])
                keys.append(key)

        # removing some subjects (not definitive)
        if len(keys) > 1:
            candidate = [b for a,b in zip(keys, s_candidates) if " " in a]
            if candidate:
                s_candidates = [candidate.pop()]
            else:
                s_candidates = [s_candidates.pop()]

        if verb == "be" and prep == DEFAULT_VERB:
            # the case of the verb to be has to be treated different from the rest
            objct = get_dbo_class(objct, cla_lex_table)
            o_candidates = [objct]
            pred = prop_lex_table[verb][prep]
        else:
            # NER the object
            o_candidates = []
            for key in term_URI_dict.keys():
                if key in objct.lower():
                    if key != "the":
                        o_candidates.append(term_URI_dict[key])

            # Lexicalization predicate        
            if verb in prop_lex_table:
                if prep in prop_lex_table[verb]:
                    if prop_lex_table[verb][prep] == UNKOWN_VALUE:
                        pred = prop_lex_table[verb][DEFAULT_VERB]
                    else:
                        pred = prop_lex_table[verb][prep]

                else:
                    pred = prop_lex_table[verb][DEFAULT_VERB]
            else:
                pred = Literal(orginal_pred)
            
        # Build triple

        for s in s_candidates:
            for o in o_candidates:
                if isinstance(pred,list):
                    # temporal fix, to be changed
                    # pred = pred.pop()
                    pred = get_best_candidate(s, o, pred, term_types_dict, dbo_graph)
                else:
                    if not isinstance(pred, Literal):
                        pred = URIRef(pred)
                if not isinstance(o, Literal):
                    o = URIRef(o)

                new_triple = triple.get_copy()
                new_triple.set_rdf_triples(URIRef(s),pred,o)
                new_triples.append(new_triple)

    return new_triples

def get_best_candidate(subj, objct, candidates, term_types_dict, dbo_graph):

    # get list of classes of elems

    subj = [URIRef(x) for x in term_types_dict[subj]]
    objct = [URIRef(x) for x in term_types_dict[objct]] 

    scores = []
    for candidate in candidates:
        score = 0
        candidate = URIRef(candidate)
        p_range = dbo_graph.value(subject=candidate, predicate=RDFS.range)
        p_domain = dbo_graph.value(subject=candidate, predicate=RDFS.domain)
        if p_domain in subj:
            score = score + 1
        elif p_range in objct:
            score = score + 1
        scores.append(score)

    best_score = max(scores)
    result = candidates[scores.index(best_score)]
    return URIRef(result)
    
def get_dbo_class(objct, cla_lex_table):
    """ Function that returns a dbo class given a text, for the to be case """
    objct = objct.lower()
    if objct in cla_lex_table.keys():
        return URIRef(cla_lex_table[objct])
    else:
        candidates = []
        temp_obj = objct.split(" ")
        for k in cla_lex_table.keys():
            if k in temp_obj:
                candidates.append(k)
        # strategy to select best candidate
        if candidates:
            key = candidates.pop()
            result = cla_lex_table[key]
            return URIRef(result)
        else:
            return Literal(objct)

def build_result_graph(triples):
    """ Builds a rdf graph with the result triples """
    g = Graph()
    for triple in triples:
        triple.get_rdf_triple()
        g.add((triple.subj_rdf, triple.pred_rdf, triple.objct_rdf))
    result = g.serialize(format='ttl')
    return result

def save_result_graph(triples, fpath):
    """ Builds a rdf graph with the result triples """
    g = Graph()
    for triple in triples:
        triple.get_rdf_triple()
        g.add((triple.subj_rdf, triple.pred_rdf, triple.objct_rdf))
    try:
        g.serialize(fpath,format='ttl')
    except:
        print(f"Error while saving the graph in{fpath}")
        exit()
    result = g.serialize(format='ttl')
    return result
