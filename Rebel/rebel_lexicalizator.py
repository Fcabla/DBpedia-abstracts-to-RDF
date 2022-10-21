import pandas as pd
import json
import requests
import tqdm
import re

SPOTLIGHT_ONLINE_API = "https://api.dbpedia-spotlight.org/en/annotate"
SPOTLIGHT_LOCAL_API = "https://api.dbpedia-spotlight.org/en/annotate"
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

        if 'Resources' in decoded:
            for dec in decoded['Resources']:
                term_URI_dict[dec['@surfaceForm']] = dec['@URI']
                term_types_dict[dec['@URI']] = dec['@types'].split(",")

            if dbpedia_only:
                for key, value in term_types_dict.items():
                    value = [x.replace('dbpedia:', 'https://dbpedia.org/ontology/') for x in value if "DBpedia:" in x]
                    term_types_dict[key] = value

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
            print(f'falied lexicalization of: [{elem}]. Posibles candidates are:  [{[(candidate, term_URI_dict[candidate]) for candidate in candidates]}]')
            
    return result

def get_rdf_triples(abstract, relations, lex_table):
    relations = relations.strip('][')
    relations = relations.replace("', '","\n")
    relations = relations[1:-1]
    abstract_dict, _ = get_annotated_text_dict(abstract, service_url=SPOTLIGHT_LOCAL_API, confidence=0.3, support=0, dbpedia_only=True)
    relations_dict, _ = get_annotated_text_dict(relations, service_url=SPOTLIGHT_LOCAL_API, confidence=0.3, support=0, dbpedia_only=True)
    term_URI_dict = {**abstract_dict, **relations_dict}
    print(term_URI_dict)
    rdf_triples = []
    relations = relations.split('\n')
    for relation in relations:
        print(relation)
        relation =  re.sub('\s\|\s', '|', relation)
        triplet = relation.split('|')
        subj = triplet[0]
        prop = triplet[1]
        obj = triplet[2]
        
        subj = replace_text_URI(subj, term_URI_dict)
        try:
            prop = lex_table['prop']
        except:
            prop = None
        obj = replace_text_URI(obj, term_URI_dict)

        if subj != None and prop != None and obj != None:
            rdf_triples.append(f'{subj}|{prop}|{obj}')
    return rdf_triples

def main():
    try:
        with open(LEX_PATH) as json_file:
            lex_table = json.load(json_file)
        json_file.close()
    except:
        print(f"Error while parsing the {LEX_PATH} file, please check if the folder file is reacheable and if the path is correct")
        exit()

    df = pd.read_csv('Rebel/results/rebel_triples.csv')
    df = df[0:3]
    df = df.to_dict(orient='records')
    for elem in tqdm.tqdm(df):
        elem['rdf_triples'] = get_rdf_triples(elem['abstract'], elem['relations'], lex_table)
    df = pd.DataFrame.from_records(df)
    df.to_csv(f'Rebel/rebel_triples_rdf.csv')

if __name__ == "__main__":
    main()