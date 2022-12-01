"""
Script to translate text triplets obtained from REBEL (main_rebel.py) into RDF triplets.
In order to perform the lexicalization we use DBpedia Spotlight and a lexicalization table (lexicalization_properties.json)

Rebel paper: https://aclanthology.org/2021.findings-emnlp.204.pdf
Rebel repo: https://github.com/babelscape/rebel
Author: Fernando Casabán Blasco
"""

import pandas as pd
import json
import requests
import tqdm
import re
import random
import logging
from rdflib import Literal, XSD

# Global variables
SPOTLIGHT_ONLINE_API = "https://api.dbpedia-spotlight.org/en/annotate"
SPOTLIGHT_LOCAL_API = "http://localhost:2222/rest/annotate/"
LEX_PATH = "Rebel\lexicalization_properties.json"
# Properties with literal objects
PROPERTIES_DATES = ["http://www.wikidata.org/wiki/Property:P1191", "http://dbpedia.org/ontology/startDate", "http://www.wikidata.org/wiki/Property:P576", "http://dbpedia.org/ontology/birthDate", "http://dbpedia.org/ontology/deathDate", "http://dbpedia.org/ontology/publicationDate", "http://dbpedia.org/ontology/startDateTime", "http://dbpedia.org/ontology/endDateTime", ]
PROPERTIES_YEARS = ["http://www.wikidata.org/wiki/Property:P585", "http://www.wikidata.org/wiki/Property:P571"]
PROPERTIES_INTEGERS = ["http://dbpedia.org/ontology/numberOfPeopleAttending", "http://dbpedia.org/ontology/numberOfEpisodes"]

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

def replace_text_URI(elem, term_URI_dict, pos):
    """Function that replaces an element of a triplet (subject or object) into a resource/literal from DBpedia ont"""
    case = ''
    result = None

    # Check if the elem is perfectly equal to a property lexicalization
    if elem in term_URI_dict:
        result = term_URI_dict[elem]
        case = 'A' # Perfect match
    else:
        # Check if there are lexicalizations that unperfectly match with our element.
        # For example we have as elem 'Rafa Nadal' but the lexicalization is for just 'Nadal'
        candidates = []
        for cand in term_URI_dict:
            if cand in elem:
                candidates.append(cand)

        for candidate in candidates:
            # check if any candidate can be matched using the URI
            # For example, we have as elem 'president of the united states' but the lexicalization is 'president'.
            #   But the URI of the lexicalization is: 'dbpedia/resource/President_of_the_United_States'
            lexicalization = term_URI_dict[candidate]
            lexicalization = lexicalization.replace("http://dbpedia.org/resource/", "")
            lexicalization = re.sub('\_', ' ', lexicalization)
            if elem.lower() == lexicalization.lower():
                result = term_URI_dict[candidate]
                case = 'D' # Imperfect match, found a lexicalization in the URI
                break
        if result == None:
            # No lexicalization found
            if candidates:
                case = 'C' # failed match, found candidates but none worked
            else:
                case = 'B' # failed match, not candidates found
            logging.debug(f'falied lexicalization of {pos}: [{elem}]. Posibles candidates are:  [{[(candidate, term_URI_dict[candidate]) for candidate in candidates]}]')
            #print(f'falied lexicalization of: [{elem}]. Posibles candidates are:  [{[(candidate, term_URI_dict[candidate]) for candidate in candidates]}]')
    return result, case

def replace_text_URI_any(elem, term_URI_dict):
    """Function that replaces an element of a triplet (subject or object) into a resource/literal from DBpedia ont.
    Imperfect matches count as correct: For example we have as elem 'Rafa Nadal' but the lexicalization is for just 'Nadal'
    """
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
    """Function that replaces an element of a triplet (subject or object) into a resource/literal from DBpedia ont.
    Just perfect matches count as correct"""
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
    """Function that querys DBpedia Spotlight with the abstract and text triplets and perform the substitution 
    of the text triplets elements with the lexicalized elements"""

    # Initialize log of different cases
    cases_count = {'A': 0,'B': 0,'C': 0,'D': 0,'E':0,'F':0}
    # Turn relations from string into a list of strings
    relations = relations.strip('][')
    relations = relations.replace("', '","\n")
    relations = relations[1:-1]
    # Query DBpedia Spotlight with abstract and text triplets
    abstract_dict = get_annotated_text_dict(abstract, service_url=SPOTLIGHT_LOCAL_API, confidence=0.3, support=0, dbpedia_only=True)
    relations_dict = get_annotated_text_dict(relations, service_url=SPOTLIGHT_LOCAL_API, confidence=0.3, support=0, dbpedia_only=True)
    if abstract_dict == None:
        # Error 414, request too long
        term_URI_dict = relations_dict
    elif relations_dict == None:
        # Error 414, request too long
        term_URI_dict = abstract_dict
    else:
        # Join both dicts
        term_URI_dict = {**abstract_dict, **relations_dict}

    rdf_triples = []
    relations = relations.split('\n')
    for relation in relations:
        # For each relation extract the elements
        relation =  re.sub('\s\|\s', '|', relation)
        triplet = relation.split('|')
        subj = triplet[0]
        prop = triplet[1]
        obj = triplet[2]
        # Lexicalize the subject
        subj, case = replace_strategy(subj, term_URI_dict, 'subj')
        cases_count[case] += 1
        try:
            # Lexicalize the property
            prop = lex_table[prop]
        except:
            # Property lexicalization error. TODO: FIND why sometimes we get this error
            # e.g. from 'position held' we obtain sometimes position
            prop_candidates = [key for key in lex_table.keys() if prop in key]
            if len(prop_candidates) == 1:
                prop = lex_table[prop_candidates[0]]
            else:
                cases_count['E'] += 1 # Error in property
                #print(prop)
                #print(prop, prop_candidates)
                prop = None
        # Check property type so we can process the object as resource or literal
        prop_type = None
        if prop in PROPERTIES_DATES:
            prop_type = XSD.date
        elif prop in PROPERTIES_INTEGERS:
            prop_type = XSD.nonNegativeInteger
        elif prop in PROPERTIES_YEARS:
            candidates = re.findall(r'\b\d{3}\b|\b\d{4}\b', obj)
            if candidates:
                obj = max(candidates, key=len)
                obj = f'http://dbpedia.org/resource/{obj}'
            else:
                obj = Literal(obj)

        if prop_type:
            # Lexicalize the object as literal
            try:
                obj = Literal(obj, datatype=prop_type)
            except:
                obj = Literal(obj)
            cases_count['F'] += 1
        if obj == triplet[2]:
            # Lexicalize the object as resource
            obj, case = replace_strategy(obj, term_URI_dict, 'obj')
            cases_count[case] += 1
        # Store just the triplets that lexicalization have been found for the 3 elements of the text triplet
        if subj != None and prop != None and obj != None:
            rdf_triples.append(f'{subj}|{prop}|{obj}')
        else:
            logging.debug(f'falied lexicalization {subj} | {prop} | {obj}')

    return rdf_triples, cases_count

def main():
    # Logging stuff
    logging.basicConfig(handlers=[logging.FileHandler(filename='Rebel/results/errors2.log', encoding='utf-8', mode='a+')],level=logging.DEBUG)
    # Load lexicalization lookup table
    try:
        with open(LEX_PATH) as json_file:
            lex_table = json.load(json_file)
        json_file.close()
    except:
        print(f"Error while parsing the {LEX_PATH} file, please check if the folder file is reacheable and if the path is correct")
        exit()
    # Load csv with text triplets
    df = pd.read_csv('Rebel/results/rebel_triples.csv')
    #df = df[0:2]
    df = df.to_dict(orient='records')
    # Track every case
    total_cases_count = {'A': 0,'B': 0,'C': 0,'D': 0,'E':0,'F':0}
    tracker = 0
    for elem in tqdm.tqdm(df):
        elem['rdf_triples'], cases_count = get_rdf_triples(elem['abstract'], elem['relations'], lex_table, replace_strategy=replace_text_URI)
        for key,value in cases_count.items():
            total_cases_count[key] += value
        if tracker % 1000 == 0:
            print()
            print(tracker, total_cases_count)
        tracker += 1
    # Store results into a dataframe
    df = pd.DataFrame.from_records(df)
    print("END")
    print(total_cases_count)
    df.to_csv(f'Rebel/results/rebel_triples_rdf_othertypes1.csv')

if __name__ == "__main__":
    main()