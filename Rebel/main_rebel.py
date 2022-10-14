"""
# Test to transform text to RDF by using a relation extraction model (REBEL)

# Rebel paper: https://aclanthology.org/2021.findings-emnlp.204.pdf
# Rebel repo: https://github.com/babelscape/rebel
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
import tqdm

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

def run_rebel(input_sentence, gen_kwargs=None):
    # Load model and tokenizer
    tokenizer = AutoTokenizer.from_pretrained("Babelscape/rebel-large")
    model = AutoModelForSeq2SeqLM.from_pretrained("Babelscape/rebel-large")
    if gen_kwargs == None:
        gen_kwargs = {
            "max_length": 256, #max_length – (optional) int The max length of the sequence to be generated. Between min_length and infinity. Default to 20.
            "length_penalty": 0, #length_penalty – (optional) float Exponential penalty to the length. Default to 1.
            "num_beams": 3, #num_beams – (optional) int Number of beams for beam search. Must be between 1 and infinity. 1 means no beam search. Default to 1.
            "num_return_sequences": 3, # num_return_sequences – (optional) int The number of independently computed returned sequences for each element in the batch. Default to 1.
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

def pipeline(input_sentence="", use_correferences = False, by_sent = False, gen_kwargs = None):
    #input_sentence = "Gràcia is a district of the city of Barcelona, Spain. It comprises the neighborhoods of Vila de Gràcia, Vallcarca i els Penitents, El Coll, La Salut and Camp d'en Grassot i Gràcia Nova. Gràcia is bordered by the districts of Eixample to the south, Sarrià-Sant Gervasi to the west and Horta-Guinardó to the east. A vibrant and diverse enclave of Catalan life, Gràcia was an independent municipality for centuries before being formally annexed by Barcelona in 1897 as a part of the city's expansion."
    #input_sentence = "Barack Hussein Obama II is an American politician who is the 44th and current President of the United States. He is the first African American to hold the office and the first president born outside the continental United States. Born in Honolulu, Hawaii, Obama is a graduate of Columbia University and Harvard Law School, where he was president of the Harvard Law Review. He was a community organizer in Chicago before earning his law degree. He worked as a civil rights attorney and taught constitutional law at the University of Chicago Law School between 1992 and 2004. While serving three terms representing the 13th District in the Illinois Senate from 1997 to 2004, he ran unsuccessfully in the Democratic primary for the United States Hou"

    if use_correferences:
        nlp_ref = spacy.load("en_core_web_trf")
        nlp_ref.add_pipe('coreferee')
        doc = nlp_ref(input_sentence)
        input_sentence = resolve_correferences(doc)
    
    if by_sent:
        nlp_sents = spacy.load("en_core_web_sm")
        doc = nlp_sents(input_sentence)
        input_sentence = [sent.text for sent in doc.sents]

    triplets = run_rebel(input_sentence, gen_kwargs)

    # TEXT TRIPLES TO RDF TRIPLES
    # ...

    return triplets
    

def pipeline_hf(from_index, to_index):
    df = pd.read_csv('datasets/long-abstracts-sample.csv')
    try:
        df = df[from_index:to_index]
    except:
        print("Index errors")
        exit()
    
    df = df.to_dict(orient='records')

    gen_kwargs = {
        "max_length": 1024,
        "length_penalty": 10,
        "num_beams": 10,
        "num_return_sequences": 10,
    }

    for elem in tqdm.tqdm(df):
        try:
            elem['relations'] = pipeline(elem['abstract'], use_correferences = False, by_sent = False, gen_kwargs = gen_kwargs)
        except:
            print('error')
            elem['relations'] = ['None']
    
    df = pd.DataFrame.from_records(df)
    
    df.to_csv(f'Rebel/results/rebel_triplets{from_index}_{to_index}.csv')
        #{'individual': 'http://dbpedia.org/resource/Lefkogeia', 'abstract': 'Lefkogeia (Greek: Λευκόγεια) is a village in the municipal unit of Foinikas, Rethymno regional unit, Crete, Greece. The village has 289 inhabitants.', 'test': 'Lefko'}

def main():    
    pipeline_hf(0,1000)

if __name__ == "__main__":
    main()
    