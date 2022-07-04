import requests
import json
import time
from rdflib import Graph, RDFS, URIRef, Literal
from utils.log_generator import triple_with_no_uri_log, triple_with_no_uri_log_subject, triple_with_no_uri_log_object, triple_with_no_uri_log_object2
import string

SPOTLIGHT_ONLINE_API = "https://api.dbpedia-spotlight.org/en/annotate"
UNKOWN_VALUE = "UNK"
DEFAULT_VERB = "DEF"

###############
# Text to RDF #
###############


def get_annotated_text_dict(text, service_url=SPOTLIGHT_ONLINE_API, confidence=0.3, support=0, dbpedia_only=True):
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
        resp = requests.get(service_url, params=parameters, headers=headerinfo)
    except:
        if service_url == SPOTLIGHT_ONLINE_API:
            print("Error at dbpedia spotlight api")
            return None
        try:
            print("Error at local dbpedia spotlight, trying with the api one")
            resp = requests.get(SPOTLIGHT_ONLINE_API, params=parameters, headers=headerinfo)
        except:
            print("Error at dbpedia spotlight api")
            return None

    if resp.status_code != 200:
        print(f"error, status code: {resp.status_code}")
        return None
    else:
        decoded = json.loads(resp.text)

        if 'Resources' in decoded:
            for dec in decoded['Resources']:
                term_URI_dict[dec['@surfaceForm']] = dec['@URI']
                term_types_dict[dec['@URI']] = dec['@types'].split(",")

            if dbpedia_only:
                for key, value in term_types_dict.items():
                    value = [x.replace('dbpedia:', 'https://dbpedia.org/ontology/') for x in value if "DBpedia:" in x]
                    term_types_dict[key] = value

    return term_URI_dict, term_types_dict


def load_dbo_graph(dbo_path):
    """ Return the ontology as a rdflib graph """
    try:
        g = Graph()
        g.parse(dbo_path)
    except:
        print(f"Error while parsing the {dbo_path} file (dbpedia ontology file), please check if the file is in a "
              f"recheable folder and if the path is correct")
        exit()
    return g


def is_word(entity, obj_text):
    """ Check if entity maps with a word or group of words in obj_text """
    pos = obj_text.find(entity.lower())
    satisfy_left = True
    if pos != 0:  # entity not situated at the beginning of the obj_text
        char_left = obj_text[pos - 1]
        satisfy_left = (char_left == ' ' or char_left in string.punctuation)
    satisfy_right = True
    if pos + len(entity) != len(obj_text):    # entity not situated at the end of the obj_text
        char_right = obj_text[pos + len(entity)]
        satisfy_right = (char_right == ' ' or char_right in string.punctuation)
    return satisfy_left and satisfy_right


def replace_text_URI(triples, term_URI_dict, term_types_dict, prop_lex_table, cla_lex_table, dbo_graph):
    """
    Maybe this function should be inside the triple class
    """
    new_triples = []
    timestr = time.strftime("%Y%m%d-%H%M")

    for triple in triples:
        subj_text = [x for x in triple.subj if x.dep_ != "det"]
        subj_text = ' '.join([x.text.lower() for x in subj_text])
        obj_text = ' '.join([x.text.lower() for x in triple.objct])
        verb = triple.pred[0].lemma_
        if len(triple.pred) == 2:  # Extract preposition from pred
            prep = triple.pred[1].text.lower()
        else:
            prep = DEFAULT_VERB

        # URI for the subject
        # We select the entities included in the subject
        entity_selected_subj = []
        for entity in term_URI_dict.keys():
            if entity.lower() in subj_text:
                if is_word(entity, subj_text):
                    entity_selected_subj.append(entity)
        # If more than one candidate, we take the longest one
        if entity_selected_subj:
            if len(entity_selected_subj) > 1:
                entity_name = max(entity_selected_subj, key=len)
            else:
                entity_name = entity_selected_subj[0]
        else:
            triple_with_no_uri_log_subject(triple, subj_text)
            continue
        subject_URI = term_URI_dict[entity_name]
        subject_RDF = URIRef(subject_URI)

        if verb == "be" and prep == DEFAULT_VERB:
            pred_URI = prop_lex_table[verb][prep]
            pred_RDF = URIRef(pred_URI)
            object_URI = get_dbo_class(obj_text, cla_lex_table)  # returns a unique URIRef or Literal
            if isinstance(object_URI, Literal):
                triple_with_no_uri_log_object(triple, obj_text)  # save object Literal in log file
                continue
            else:
                object_RDF = URIRef(object_URI)

            # Build triple. RDF triples are made up by URI references or Literals
            new_triple = triple.get_copy()
            new_triple.set_rdf_triples(subject_RDF, pred_RDF, object_RDF)
            new_triples.append(new_triple)
        else:
            # Lexicalization predicate (verb is not 'to be')
            if verb in prop_lex_table:
                if prep in prop_lex_table[verb]:
                    if prop_lex_table[verb][prep] == UNKOWN_VALUE:
                        pred_URI = prop_lex_table[verb][DEFAULT_VERB]
                    else:
                        pred_URI = prop_lex_table[verb][prep]
                else:
                    pred_URI = prop_lex_table[verb][DEFAULT_VERB]
            else:
                pred_URI = Literal(verb)

            if (pred_URI == UNKOWN_VALUE) | (isinstance(pred_URI, Literal)):
                # save object Literal in log file
                triple_with_no_uri_log(triple, verb)
                continue

            # select mentions in the object identified by DBpedia Spotlight
            entity_selected_obj = []
            for entity in term_URI_dict.keys():
                if entity.lower() in obj_text:
                    if is_word(entity, obj_text) and entity.lower() != "the":
                        entity_selected_obj.append(entity)

            # Build triples
            if entity_selected_obj:
                for entity_name in entity_selected_obj:
                    object_URI = term_URI_dict[entity_name]
                    object_RDF = URIRef(object_URI)

                    # Select the appropriate URI for the pred
                    if isinstance(pred_URI, list):
                        if object_URI:
                            pred_RDF = get_best_candidate(subject_URI, object_URI, pred_URI, term_types_dict, dbo_graph)
                        else:
                            pred_RDF = URIRef(pred_URI[0])
                    else:
                        if not isinstance(pred_URI, Literal):
                            pred_RDF = URIRef(pred_URI)

                    new_triple = triple.get_copy()
                    new_triple.set_rdf_triples(subject_RDF, pred_RDF, object_RDF)
                    new_triples.append(new_triple)
            # no mentions identified by DBpedia Spotlight. object is literal
            else:
                triple_with_no_uri_log_object2(triple, obj_text)  # save object Literal in log file
                object_URI = None
                object_RDF = Literal(obj_text)

                # Select the appropriate URI for the pred
                if isinstance(pred_URI, list):
                    pred_RDF = URIRef(pred_URI[0])
                else:
                    if not isinstance(pred_URI, Literal):
                        pred_RDF = URIRef(pred_URI)

                # Build triple. RDF triples are made up by URI references or Literals
                new_triple = triple.get_copy()
                new_triple.set_rdf_triples(subject_RDF, pred_RDF, object_RDF)
                new_triples.append(new_triple)

    return new_triples


def get_best_candidate(subj, objct, preds_uri, term_types_dict, dbo_graph):
    # extract path from the URI, to avoid problems when using different schemas (http or https)
    subj_path = [x.partition("//")[2] for x in term_types_dict[subj]]
    objt_path = [x.partition("//")[2] for x in term_types_dict[objct]]

    scores = []
    for uri in preds_uri:
        score = 0
        uri = uri.replace("https:", "http:")  # URIs in ontology follow schema http
        uri = URIRef(uri)

        # get range and domain from rdf graph
        if pred_domain := dbo_graph.value(subject=uri, predicate=RDFS.domain):
            pred_domain_path = pred_domain.partition("//")[2]
            # rdfs:domain states the classes that a subject with this property must match (at least one)
            if pred_domain_path in subj_path:
                score += 1

        if pred_range := dbo_graph.value(subject=uri, predicate=RDFS.range):
            pred_range_path = pred_range.partition("//")[2]
            # rdfs:range states the classes that an object with this predicate must match (at least one)
            if pred_range_path in objt_path:
                score += 1
        scores.append(score)

    best_score = max(scores)
    return URIRef(preds_uri[scores.index(best_score)])


def get_dbo_class(objct, cla_lex_table):
    """ Function that returns a dbo class given a text, for the to be case """
    if objct in cla_lex_table.keys():
        return cla_lex_table[objct]
    else:
        temp_obj = objct.split(" ")
        candidates = [k for k in cla_lex_table.keys() if k in temp_obj]
        # strategy to select best candidate
        if candidates:
            key = candidates.pop()
            result = cla_lex_table[key]
            return result
        else:
            return Literal(objct)


def build_result_graph(triples):
    """ Builds a rdf graph with the result triples """
    g = Graph()
    for triple in triples:
        g.add((triple.subj_rdf, triple.pred_rdf, triple.objct_rdf))
    result = g.serialize(format='ttl')
    return g, result
