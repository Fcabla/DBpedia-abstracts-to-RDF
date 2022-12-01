"""
Test to transform text to RDF by using a relation extraction model (REBEL)
If you are reading this, you can just skip this file since its the first approach using REBEL.
We compared different values for the REBEL model.
We also compared differente sources of the SAME model and obtained differente results.

Rebel paper: https://aclanthology.org/2021.findings-emnlp.204.pdf
Rebel repo: https://github.com/babelscape/rebel
Author: Fernando Casabán Blasco
"""

import spacy
import spacy_component
import re
import coreferee
from transformers import pipeline
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
import time

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

def rebel_transformers(input_sentence, by_sent = False):
    """ Function to perform inference on the REBEL model using transformers library using pipeline"""
    # Inference
    triplet_extractor = pipeline('text2text-generation', model='Babelscape/rebel-large', tokenizer='Babelscape/rebel-large')
    # optional: split text into sentences
    results = []
    if by_sent:
        for sent in input_sentence:
            extracted_text = triplet_extractor.tokenizer.batch_decode([triplet_extractor(sent, return_tensors=True, return_text=False)[0]["generated_token_ids"]])
            extracted_triplets = extract_triplets(extracted_text[0])
            for triplet in extracted_triplets:
                results.append(f'{triplet["head"]}|{triplet["type"]}|{triplet["tail"]}')
                #print(f'{triplet["head"]}|{triplet["type"]}|{triplet["tail"]}')
    else:
        extracted_text = triplet_extractor.tokenizer.batch_decode([triplet_extractor(input_sentence, return_tensors=True, return_text=False)[0]["generated_token_ids"]])
        extracted_triplets = extract_triplets(extracted_text[0])
        for triplet in extracted_triplets:
            results.append(f'{triplet["head"]}|{triplet["type"]}|{triplet["tail"]}')
            #print(f'{triplet["head"]}|{triplet["type"]}|{triplet["tail"]}')
    return results

def rebel_spacy(input_sentence, by_sent = False):
    """ Function to perform inference on the REBEL model using spacy as source for the model"""
    # Load the model and add rebel to the pipeleine
    nlp = spacy.load("en_core_web_sm")
    nlp.add_pipe("rebel", after="senter", config={
        'device':-1, # Number of the GPU, -1 if want to use CPU
        'model_name':'Babelscape/rebel-large'} # Model used, will default to 'Babelscape/rebel-large' if not given
        )

    # optional: split text into sentences
    results = []
    if by_sent:
        for sent in input_sentence:
            doc = nlp(sent)
            doc_list = nlp.pipe([sent])
            results = []
            for value, rel_dict in doc._.rel.items():
                results.append(f"{rel_dict['head_span']}|{rel_dict['relation']}|{rel_dict['tail_span']}")
                #print(f"{value}: {rel_dict['head_span']}|{rel_dict['relation']}|{rel_dict['tail_span']}")
    else:
        doc = nlp(input_sentence)
        doc_list = nlp.pipe([input_sentence])
        results = []
        for value, rel_dict in doc._.rel.items():
            results.append(f"{rel_dict['head_span']}|{rel_dict['relation']}|{rel_dict['tail_span']}")
            #print(f"{value}: {rel_dict['head_span']}|{rel_dict['relation']}|{rel_dict['tail_span']}")
    return results

def rebel_transformers2(input_sentence, gen_kwargs=None, by_sent = False):
    """ Function to perform inference on the REBEL model using transformers library manually"""
    # Load model and tokenizer
    tokenizer = AutoTokenizer.from_pretrained("Babelscape/rebel-large")
    model = AutoModelForSeq2SeqLM.from_pretrained("Babelscape/rebel-large")
    if gen_kwargs == None:
        print('aa')
        gen_kwargs = {
            "max_length": 256,
            "length_penalty": 0,
            "num_beams": 3,
            "num_return_sequences": 3,
        }

    # Text to extract triplets from
    text = input_sentence

    # Tokenizer text
    model_inputs = tokenizer(text, max_length=256, padding=True, truncation=True, return_tensors = 'pt')

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
    return results

def print_triplets(triplets, uniques=True):
    if uniques:
        triplets = list(set(triplets))
    print('-'*50)
    for triplet in triplets:
        print(triplet)
    return len(triplets)

def main():
    # Test with different sentences
    input_sentence = "Gràcia is a district of the city of Barcelona, Spain. It comprises the neighborhoods of Vila de Gràcia, Vallcarca i els Penitents, El Coll, La Salut and Camp d'en Grassot i Gràcia Nova. Gràcia is bordered by the districts of Eixample to the south, Sarrià-Sant Gervasi to the west and Horta-Guinardó to the east. A vibrant and diverse enclave of Catalan life, Gràcia was an independent municipality for centuries before being formally annexed by Barcelona in 1897 as a part of the city's expansion."
    input_sentence = "Barack Hussein Obama II is an American politician who is the 44th and current President of the United States. He is the first African American to hold the office and the first president born outside the continental United States. Born in Honolulu, Hawaii, Obama is a graduate of Columbia University and Harvard Law School, where he was president of the Harvard Law Review. He was a community organizer in Chicago before earning his law degree. He worked as a civil rights attorney and taught constitutional law at the University of Chicago Law School between 1992 and 2004. While serving three terms representing the 13th District in the Illinois Senate from 1997 to 2004, he ran unsuccessfully in the Democratic primary for the United States Hou"

    # Preprocessing options
    use_correferences = False
    by_sent = False
    if use_correferences:
        print("Using correferences")
        nlp_ref = spacy.load("en_core_web_trf")
        nlp_ref.add_pipe('coreferee')
        doc = nlp_ref(input_sentence)
        input_sentence = resolve_correferences(doc)
    
    if by_sent:
        nlp_sents = spacy.load("en_core_web_sm")
        doc = nlp_sents(input_sentence)
        input_sentence = [sent.text for sent in doc.sents]
        
    #triplets = rebel_transformers(input_sentence)
    #print_triplets(triplets)
    #triplets = rebel_spacy(input_sentence, by_sent=by_sent)
    #print_triplets(triplets)

    # Test with different values for the hyperparameters
    for lp in [0, 1, 5, 10]:
        for nrs in [3, 4, 5, 10, 20, 30]:
            # measure inference time
            tme = time.time()
            gen_kwargs = {
                "max_length": 1024,
                "length_penalty": lp,
                "num_beams": nrs,
                "num_return_sequences": nrs
            }
            triplets = rebel_transformers2(input_sentence, gen_kwargs, by_sent=by_sent)
            num_triplets = print_triplets(triplets)
            tme = time.time() - tme
            print(f'lp: {lp}, nrs: {nrs}, len: {num_triplets}, time: {tme}')

if __name__ == "__main__":
    main()






