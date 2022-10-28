import pandas as pd
import json
import requests
import tqdm
import re
import random
import logging

SPOTLIGHT_ONLINE_API = "https://api.dbpedia-spotlight.org/en/annotate"
SPOTLIGHT_LOCAL_API = "http://localhost:2222/rest/annotate/"
LEX_PATH = "Rebel\lexicalization_properties.json"
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
        term_URI_dict = {}
        term_types_dict = {}
        if 'Resources' in decoded:
            for dec in decoded['Resources']:
                term_URI_dict[dec['@surfaceForm']] = dec['@URI']
                term_types_dict[dec['@URI']] = dec['@types'].split(",")

            if dbpedia_only:
                for key, value in term_types_dict.items():
                    value = [x.replace('dbpedia:', 'https://dbpedia.org/ontology/') for x in value if "DBpedia:" in x]
                    term_types_dict[key] = value
    return term_URI_dict
    return term_URI_dict, term_types_dict

def replace_text_URI(elem, term_URI_dict):

    result = None
    # Perfect match
    if elem in term_URI_dict:
        result = term_URI_dict[elem]
    else:
        candidates = []
        for cand in term_URI_dict:
            if cand in elem:
                candidates.append(cand)

        for candidate in candidates:
            lexicalization = term_URI_dict[candidate]
            lexicalization = lexicalization.replace("http://dbpedia.org/resource/", "")
            lexicalization = re.sub('\_', ' ', lexicalization)
            if elem.lower() == lexicalization.lower():
                result = term_URI_dict[candidate]
                break
        if result == None:
            logging.debug(f'falied lexicalization of: [{elem}]. Posibles candidates are:  [{[(candidate, term_URI_dict[candidate]) for candidate in candidates]}]')
            #print(f'falied lexicalization of: [{elem}]. Posibles candidates are:  [{[(candidate, term_URI_dict[candidate]) for candidate in candidates]}]')
    return result

def replace_text_URI_any(elem, term_URI_dict):
    result = None
    # Perfect match
    if elem in term_URI_dict:
        result = term_URI_dict[elem]
    else:
        candidates = []
        for cand in term_URI_dict:
            if cand in elem:
                candidates.append(cand)
        if candidates:
            result = term_URI_dict[random.choice(candidates)]
        if result == None:
            pass
            #print(f'falied lexicalization of: [{elem}]. Posibles candidates are:  [{[(candidate, term_URI_dict[candidate]) for candidate in candidates]}]')
    return result

def replace_text_URI_exact(elem, term_URI_dict):
    result = None
    # Perfect match
    if elem in term_URI_dict:
        result = term_URI_dict[elem]
    else:
        candidates = []
        for cand in term_URI_dict:
            if cand in elem:
                candidates.append(cand)
        if result == None:
            pass
            #print(f'falied lexicalization of: [{elem}]. Posibles candidates are:  [{[(candidate, term_URI_dict[candidate]) for candidate in candidates]}]')
    return result

def get_rdf_triples(abstract, relations, lex_table, replace_strategy):
    relations = relations.strip('][')
    relations = relations.replace("', '","\n")
    relations = relations[1:-1]
    abstract_dict = get_annotated_text_dict(abstract, service_url=SPOTLIGHT_LOCAL_API, confidence=0.3, support=0, dbpedia_only=True)
    relations_dict = get_annotated_text_dict(relations, service_url=SPOTLIGHT_LOCAL_API, confidence=0.3, support=0, dbpedia_only=True)
    if abstract_dict == None:
        # Error 414, request too long
        term_URI_dict = relations_dict
    elif relations_dict == None:
        # Error 414, request too long
        term_URI_dict = abstract_dict
    else:
        term_URI_dict = {**abstract_dict, **relations_dict}

    rdf_triples = []
    relations = relations.split('\n')
    for relation in relations:
        #print(relation)
        relation =  re.sub('\s\|\s', '|', relation)
        triplet = relation.split('|')
        subj = triplet[0]
        prop = triplet[1]
        obj = triplet[2]
        
        subj = replace_strategy(subj, term_URI_dict)
        try:
            prop = lex_table[prop]
        except:
            #print('error property')
            prop = None
        obj = replace_strategy(obj, term_URI_dict)
        
        if subj != None and prop != None and obj != None:
            rdf_triples.append(f'{subj}|{prop}|{obj}')

    return rdf_triples

def main():
    logging.basicConfig(level=logging.DEBUG, filename='Rebel/results/errors.log', filemode='a')
    try:
        with open(LEX_PATH) as json_file:
            lex_table = json.load(json_file)
        json_file.close()
    except:
        print(f"Error while parsing the {LEX_PATH} file, please check if the folder file is reacheable and if the path is correct")
        exit()

    df = pd.read_csv('Rebel/results/rebel_triples.csv')
    #df = df[0:10]
    df = df.to_dict(orient='records')
    for elem in tqdm.tqdm(df):
        elem['rdf_triples'] = get_rdf_triples(elem['abstract'], elem['relations'], lex_table, replace_strategy=replace_text_URI)
    df = pd.DataFrame.from_records(df)
    #df.to_csv(f'Rebel/results/rebel_triples_rdf_exact.csv')

if __name__ == "__main__":
    main()