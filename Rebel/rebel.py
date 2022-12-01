"""
Test to transform text to RDF by using a relation extraction model (REBEL)
If you are reading this, you can just skip this file since its the first approach using REBEL.
We compared differente sources of the SAME model and obtained differente results.

Rebel paper: https://aclanthology.org/2021.findings-emnlp.204.pdf
Rebel repo: https://github.com/babelscape/rebel
Author: Fernando Casabán Blasco
"""

# IMPORTS
from transformers import pipeline
import requests
import json
import coreferee
import spacy
import re
import pandas as pd
import json
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

# from rdflib import Graph, RDFS, URIRef, Literal

# GLOBALS
SPOTLIGHT_ONLINE_API = "https://api.dbpedia-spotlight.org/en/annotate"
UNKOWN_VALUE = "UNK"
DEFAULT_VERB = "DEF"
TEST_TEXT = "Barack Hussein Obama II is an American politician who is the 44th and current President of the United States. He is the first African American to hold the office and the first president born outside the continental United States. Born in Honolulu, Hawaii, Obama is a graduate of Columbia University and Harvard Law School, where he was president of the Harvard Law Review. He was a community organizer in Chicago before earning his law degree. He worked as a civil rights attorney and taught constitutional law at the University of Chicago Law School between 1992 and 2004. While serving three terms representing the 13th District in the Illinois Senate from 1997 to 2004, he ran unsuccessfully in the Democratic primary for the United States Hou"
TEST_TEXT2 = "Gràcia is a district of the city of Barcelona, Spain. It comprises the neighborhoods of Vila de Gràcia, Vallcarca i els Penitents, El Coll, La Salut and Camp d'en Grassot i Gràcia Nova. Gràcia is bordered by the districts of Eixample to the south, Sarrià-Sant Gervasi to the west and Horta-Guinardó to the east. A vibrant and diverse enclave of Catalan life, Gràcia was an independent municipality for centuries before being formally annexed by Barcelona in 1897 as a part of the city's expansion."

# DBPEDIA SPOTLIGHT FUNCTIONS

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

# TRIPLETS FUNCTIONS
def extract_triplets(text):
    """Function to parse the generated text and extract the triplets"""
    triplets = []
    relation, subject, relation, object_ = '', '', '', ''
    text = text.strip()
    current = 'x'
    for token in text.replace("<s>", "").replace("<pad>", "").replace("</s>", "").split():
        if token == "<triplet>":
            current = 't'
            if relation != '':
                triplets.append({'head': subject.strip(), 'type': relation.strip(),'tail': object_.strip()})
                relation = ''
            subject = ''
        elif token == "<subj>":
            current = 's'
            if relation != '':
                triplets.append({'head': subject.strip(), 'type': relation.strip(),'tail': object_.strip()})
            object_ = ''
        elif token == "<obj>":
            current = 'o'
            relation = ''
        else:
            if current == 't':
                subject += ' ' + token
            elif current == 's':
                object_ += ' ' + token
            elif current == 'o':
                relation += ' ' + token
    if subject != '' and relation != '' and object_ != '':
        triplets.append({'head': subject.strip(), 'type': relation.strip(),'tail': object_.strip()})
    return triplets

def resolve_correferences(doc):
    """Function to resolve and replace correferences in the text using spacy"""
    chains = doc._.coref_chains
    new_text = []
    for token in doc:
        new_crf = chains.resolve(token)
        # search for a new coreference which is not the same as the original token (O: States, C: States)
        if new_crf and new_crf[0].text != token.text:
            # swap the tokens
            # new_crf = [tkn for tkn in new_crf[0].subtree if tkn.dep_ == 'compound' or tkn.dep_ == 'nsubj']
            new_crf = [tkn for tkn in new_crf[0].subtree]

            #print(f'swaping {token} for {new_crf}')
            new_text.extend(new_crf)
        else:
            # no coreference detected, appending to final result
            new_text.append(token)
    new_text = ' '.join([tkn.text for tkn in new_text])
    new_text = re.sub(' \.', '.', new_text)
    new_text = re.sub(' \,', ',', new_text)
    return new_text

def p1(text, triplet_extractor):
    """Model inference using the model as it is (no preprocesing the input)"""
    extracted_text = triplet_extractor.tokenizer.batch_decode([triplet_extractor(text, return_tensors=True, return_text=False)[0]["generated_token_ids"]])
    extracted_triplets = extract_triplets(extracted_text[0])
    results = []
    for triplet in extracted_triplets:
        s = triplet["head"]
        t = triplet["type"]
        o = triplet["tail"]
        #results.append(f'{s}|{t}|{o}')
        results.append((s,t,o))
    results = list(set(results))
    return results

def p2(text, triplet_extractor, nlp):
    """Model inference after resolving correferences"""
    doc = nlp(text)
    processed_text = resolve_correferences(doc)

    extracted_text = triplet_extractor.tokenizer.batch_decode([triplet_extractor(processed_text, return_tensors=True, return_text=False)[0]["generated_token_ids"]])
    extracted_triplets = extract_triplets(extracted_text[0])
    results = []
    for triplet in extracted_triplets:
        s = triplet["head"]
        t = triplet["type"]
        o = triplet["tail"]
        #print(f'{s}|{t}|{o}')
        #results.append(f'{s}|{t}|{o}')
        results.append((s,t,o))
    results = list(set(results))
    return results

def p3(text, triplet_extractor, nlp):
    """Model inference after resolving correferences and splitting the text into sentences"""
    doc = nlp(text)
    processed_text = resolve_correferences(doc)

    doc = nlp(processed_text)
    sents = [sent.text for sent in doc.sents]
    results = []

    for sent in sents:
        extracted_text = triplet_extractor.tokenizer.batch_decode([triplet_extractor(sent, return_tensors=True, return_text=False)[0]["generated_token_ids"]])
        extracted_triplets = extract_triplets(extracted_text[0])
        for triplet in extracted_triplets:
            s = triplet["head"]
            t = triplet["type"]
            o = triplet["tail"]
            #print(f'{s}|{t}|{o}')
            #results.append(f'{s}|{t}|{o}')
            results.append((s,t,o))
    results = list(set(results))
    return results

def rebel_transformers2(input_sentence):
    """Model inference using transformers model manual"""
    # Load model and tokenizer
    tokenizer = AutoTokenizer.from_pretrained("Babelscape/rebel-large")
    model = AutoModelForSeq2SeqLM.from_pretrained("Babelscape/rebel-large")
    gen_kwargs = {
        "max_length": 1024,
        "length_penalty": 0,
        "num_beams": 3,
        "num_return_sequences": 3,
    }

    # Text to extract triplets from
    text = input_sentence

    # Tokenizer text
    model_inputs = tokenizer(text, max_length=1024, padding=True, truncation=True, return_tensors = 'pt')

    # Generate
    generated_tokens = model.generate(
        model_inputs["input_ids"].to(model.device),
        attention_mask=model_inputs["attention_mask"].to(model.device),
        **gen_kwargs,
    )

    # Extract text
    decoded_preds = tokenizer.batch_decode(generated_tokens, skip_special_tokens=False)

    # Extract triplets
    results = []
    for idx, sentence in enumerate(decoded_preds):
        #print(f'Prediction triplets sentence {idx}')
        sentences = extract_triplets(sentence)
        for triplet in sentences:
            results.append(f"{triplet['head']}|{triplet['type']}|{triplet['tail']}")
            #print(f"{triplet['head']}|{triplet['type']}|{triplet['tail']}")
    results = list(set(results))
    return results

def pipeline_hf():
    """Pipeline using hugging faces transformers library manual (rebel_transformers2) with a csv of 10k abstracts"""
    df = pd.read_csv('datasets/long-abstracts-sample.csv')
    df = df[:3000]
    df = df.to_dict(orient='records')
    for elem in df:
        try:
            elem['relations'] = rebel_transformers2(elem['abstract'])
        except:
            print('error')
            elem['relations'] = ['None']
    
    df = pd.DataFrame.from_records(df)
    df.to_csv('Rebel/triplets0_3000.csv')
        #{'individual': 'http://dbpedia.org/resource/Lefkogeia', 'abstract': 'Lefkogeia (Greek: Λευκόγεια) is a village in the municipal unit of Foinikas, Rethymno regional unit, Crete, Greece. The village has 289 inhabitants.', 'test': 'Lefko'}

def pipeline_bunch():
    """Pipeline using hugging faces transformers library pipeline with a csv of 10k abstracts"""
    # 1. LOAD MODELs
    nlp = spacy.load("en_core_web_trf")
    nlp.add_pipe('coreferee')
    triplet_extractor = pipeline('text2text-generation', model='Babelscape/rebel-large', tokenizer='Babelscape/rebel-large')
    
    df = pd.read_csv('datasets/long-abstracts-sample.csv')
    abstracts = df['abstract']
    samples_dict = {}
    for abstract in abstracts:
        local_results = []
        try:
            local_results.extend(p1(abstract, triplet_extractor))
            local_results.extend(p2(abstract, triplet_extractor, nlp))
            local_results.extend(p3(abstract, triplet_extractor, nlp))
            local_results = list(set(local_results))
            for triplet in local_results:
                if triplet[1] in samples_dict:
                    samples_dict[triplet[1]].append(f'{triplet[0]}|{triplet[1]}|{triplet[2]}')
                else:
                    samples_dict[triplet[1]] = [f'{triplet[0]}|{triplet[1]}|{triplet[2]}']
        except:
            print('abstract failed')
        
    with open('Rebel/samples_dict.json', 'w', encoding='utf-8') as f:
        json.dump(samples_dict, f, ensure_ascii=False, indent=4)

def pipeline_single():
    """Pipeline using hugging faces transformers library pipeline with a single abstract. 
    Comparing preprocessing steps (p1, p2 and p3 functs)"""
    # 1. LOAD MODELs
    nlp = spacy.load("en_core_web_trf")
    nlp.add_pipe('coreferee')
    triplet_extractor = pipeline('text2text-generation', model='Babelscape/rebel-large', tokenizer='Babelscape/rebel-large')
    abstract = TEST_TEXT
    print('-'*50)
    triplets = p1(abstract, triplet_extractor)
    [print(f'{triplet[0]}|{triplet[1]}|{triplet[2]}') for triplet in triplets]
    print('-'*50)

    triplets = p2(abstract, triplet_extractor, nlp)
    [print(f'{triplet[0]}|{triplet[1]}|{triplet[2]}') for triplet in triplets]
    print('-'*50)

    triplets = p3(abstract, triplet_extractor, nlp)
    [print(f'{triplet[0]}|{triplet[1]}|{triplet[2]}') for triplet in triplets]
    print('-'*50)

def main():    
    pipeline_hf()
    #pipeline_single()  
    # 2. RUN MODEL (RE)
    # We need to use the tokenizer manually since we need special tokens.
    #extracted_text = triplet_extractor.tokenizer.batch_decode([triplet_extractor(TEST_TEXT, return_tensors=True, return_text=False)[0]["generated_token_ids"]])
    #print(extracted_text[0])
    # 3. EXTRACT TEXT TRIPLES
    #extracted_triplets = extract_triplets(extracted_text[0])
    #print(extracted_triplets)
    
    # 4. RUN DBPEDIA SPOTLIGHT
    #term_URI_dict, term_types_dict = get_annotated_text_dict(TEST_TEXT)

    #for key,value in term_URI_dict.items():
    #    print(key,value)

if __name__ == "__main__":
    main()
    