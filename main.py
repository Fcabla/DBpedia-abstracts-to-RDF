import spacy
from collections import Counter
from pyclausie import ClausIE
import requests
import json

test_text = "Barack Hussein Obama II is an American politician who is the 44th and current President of the United States. He is the first African American to hold the office and the first president born outside the continental United States. Born in Honolulu, Hawaii, Obama is a graduate of Columbia University and Harvard Law School, where he was president of the Harvard Law Review. He was a community organizer in Chicago before earning his law degree. He worked as a civil rights attorney and taught constitutional law at the University of Chicago Law School between 1992 and 2004. While serving three terms representing the 13th District in the Illinois Senate from 1997 to 2004, he ran unsuccessfully in the Democratic primary for the United States Hou"
banned_subjects = ["he", "she", "it"]
SPOTLIGHT_LOCAL_URL = "http://localhost:2222/rest/annotate/"
SPOTLIGHT_ONLINE_API = "https://api.dbpedia-spotlight.org/en/annotate"

def get_parsed_text(text2parse):
    # Load model and parse text
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text2parse)
    return doc

def get_sentences(doc):
    # Extract the sentences
    sentences = []
    for sente in doc.sents:
        sentences.append(sente)
    return(sentences)

def get_clausie_instance():
    cl = ClausIE.get_instance()    
    return cl

def extract_triplets(sentences, cl):
    # Extract the triplets
    # Check if sentences is list of lists
    triples = cl.extract_triples(sentences)
    subjects = []
    predicates = []
    objects = []
    for triple in triples:
        subjects.append(triple.subject)
        predicates.append(triple.predicate)
        objects.append(triple.object)

    return(subjects,predicates,objects)

def replace_subjects(subjects):
    subj_dict = dict(sorted(Counter(subjects).items(), key=lambda item: item[1], reverse=True))
    main_subject = "undefined"
    for key, value in subj_dict.items():
        if(key.lower() not in banned_subjects):
            main_subject = key
            break

    print(f"The new subject for every triplet: {main_subject}")
    new_subjects = [main_subject for _ in range(len(subjects))]
    return(new_subjects)

def print_tuples(subjects,predicates,objects):
    for s,p,o in zip(subjects, predicates, objects):
        print(f"{s},{p},{o}")

def get_annotated_text_dict(text, service_url=SPOTLIGHT_ONLINE_API, confidence=0.3, support=0):
    headerinfo = {'Accept': 'application/json'}
    parameters = {'text': text, 'confidence': confidence, 'support': support}
    return_dict = {}
    try:
        if "localhost" in service_url:
            resp = requests.post(service_url, data=parameters, headers=headerinfo)
        else:
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
                return_dict[dec['@surfaceForm'].lower()] = dec['@URI'].lower()
    return return_dict

def replace_text_url(elements, dict):
    results = []
    for elem in elements:
        elem = elem.lower()
        if elem in dict:
            results.append(dict[elem])
        else:
            results.append(elem)
    return results

def main():
    doc = get_parsed_text(test_text)
    sentences = get_sentences(doc)

    for chk in doc.noun_chunks:
        print(chk)
    
    cl = get_clausie_instance()
    subjects, predicates, objects = extract_triplets(sentences, cl)
    new_subjects = replace_subjects(subjects)
    print_tuples(new_subjects,predicates,objects)
    spotligth_dict = get_annotated_text_dict(test_text)

    new_subjects = replace_text_url(new_subjects, spotligth_dict)
    new_objects = replace_text_url(objects, spotligth_dict)    
    print_tuples(new_subjects,predicates,new_objects)

if __name__ == "__main__":
    main()
"""
# not working well
import clause_extraction as ce

# Load model and parse text
nlp = ce.build_nlp("en_core_web_sm")
doc = nlp(test_text)

print(test_sentence._.clauses)
for clause in test_sentence._.clauses:
    print(clause.to_propositions(as_text=False, capitalize=False, inflect=None))
"""