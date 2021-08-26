from rdflib.term import URIRef
import pandas as pd
import time
import argparse

import utils.preprocess_sentences as pps
import utils.triples_extraction as te
import utils.process_triples as pt
import utils.build_RDF_triples as brt

import spacy
import coreferee

timestr = time.strftime("%Y%m%d-%H%M%S")

PROP_LEXICALIZATION_TABLE = "datasets/verb_prep_property_lookup.json"
CLA_LEXICALIZATION_TABLE = "datasets/classes_lookup.json"
DBPEDIA_ONTOLOGY = "datasets/dbo_ontology_2021.08.06.owl"
OUTPUT_FOLDER = "code/app/output/"

banned_subjects = ["he", "she", "it", "his", "hers"]
SPOTLIGHT_LOCAL_URL = "http://localhost:2222/rest/annotate/"
SPOTLIGHT_ONLINE_API = "https://api.dbpedia-spotlight.org/en/annotate"
MODIFIERS = ["compound", "amod", "nummod", "nmod", "advmod", "npadvmod"]
USE_COMPLEX_SENTENCES = False
UNKOWN_VALUE = "UNK"
DEFAULT_VERB = "DEF"

def pipeline(nlp, raw_text, dbo_graph ,prop_lex_table, cla_lex_table, use_comp_sents):
    raw_text = pps.clean_text(raw_text)
    #d1,d2 = get_dates_first_sentence(document)
    doc = nlp(raw_text)
    sentences = pps.get_sentences(doc)
    triples = te.get_all_triples(sentences, use_comp_sents)
    triples = pt.fix_xcomp_conj(triples)
    # triples = fix_aux_verbs(triples)
    triples = pt.append_preps_verbs(triples)
    triples = pt.split_conjunctions_subjs(triples)
    triples = pt.split_conjunctions_obj(triples)
    triples = pt.swap_subjects_correferences(triples, doc._.coref_chains)
    try:
        term_URI_dict, term_types_dict = brt.get_annotated_text_dict(raw_text, service_url=SPOTLIGHT_LOCAL_URL)
    except:
        return [],[]
    rdf_triples = brt.replace_text_URI(triples, term_URI_dict, term_types_dict, prop_lex_table, cla_lex_table, dbo_graph)
    return triples, rdf_triples

def print_debug(triples):
    """ Print the final result: Original sentence, text triples and rdf triples"""
    debug_info = ""
    if triples:
        sent = triples[0].sent
        debug_info += "-"*50+"  \n"
        debug_info += f"**{sent}**"
        debug_info += "  \n"
        for t in triples:
            if t.sent != sent:
                sent = t.sent
                debug_info += "  \n"
                debug_info += "-"*50+"  \n"
                debug_info += f"**{sent}**"
                debug_info += "  \n"
            debug_info += t.__repr__() + "  \n"
            debug_info += t.get_rdf_triple() + "  \n"
    return debug_info

def get_only_triples_URIs(rdf_triples):
    """ Keep just the triples that are entirely made of URIRef. """
    new_triples = []
    for t in rdf_triples:
        if isinstance(t.pred_rdf, URIRef) and isinstance(t.objct_rdf, URIRef):
            new_triples.append(t)
    return new_triples

def read_input_text(fpath):
    try:
        with open(fpath) as f:
            text = f.read()
        f.close()
    except:
        print(f"Error while reading {fpath} (input text)")
        exit()
    return text

def init():
    """ Function to load all the external components. It is supposed to run just once. """
    # Load dependency model and add coreferee support
    nlp = spacy.load("en_core_web_trf")
    nlp.add_pipe('coreferee')
    # Load datastructures
    prop_lex_table = brt.load_lexicalization_table(PROP_LEXICALIZATION_TABLE)
    cla_lex_table = brt.load_lexicalization_table(CLA_LEXICALIZATION_TABLE)
    dbo_graph = brt.load_dbo_graph(DBPEDIA_ONTOLOGY)

    return nlp, prop_lex_table, cla_lex_table, dbo_graph

if __name__ == "__main__":
    nlp, prop_lex_table, cla_lex_table, dbo_graph = init()

    print('DBpedia abstracts to RDF')
    print('This app translates any kind of text into RDF!')

    parser = argparse.ArgumentParser(description='Text to RDF parser')

    parser.add_argument('--input_text', help='Insert abstract or any other kind of text in order to generate RDF based on the input' , required=True)
    parser.add_argument('--all_sentences', help='Use all the sentences of the abstract or just use the simplest senteces (it is recommended to False)', action="store_true")
    parser.add_argument('--text_triples', help='Print the simplified sentences from the triples have been generated. This is useful to understand how the pipeline processed the input', action="store_true")
    parser.add_argument('--no_literals', help='Discard all the triples containing a literal in them. This happens when the pipeline is unable to find any lexicalization to either predicate or object', action="store_true")
    parser.add_argument('--save_debug', help='Print the text triples and RDF triples extracted for every sentence', action="store_true")
    args = parser.parse_args()

    raw_text = read_input_text(args.input_text)
    if len(raw_text) < 20:
        print("Invalid input text, try something bigger")
        exit()
    text_triples, rdf_triples = pipeline(nlp, raw_text, dbo_graph ,prop_lex_table, cla_lex_table, args.all_sentences)
    debug_info = print_debug(rdf_triples)
    if args.no_literals:
        rdf_triples = get_only_triples_URIs(rdf_triples)
    
    # save the graph
    g = brt.save_result_graph(rdf_triples,f'{OUTPUT_FOLDER}graph_{timestr}.ttl')

    # print/save rdf triples
    print("## RDF triples:")
    print('----'*5)
    rdf_triples = [t.get_rdf_triple() for t in rdf_triples]
    rdf_triples = [t.__repr__() for t in rdf_triples]
    rdf_print_triples = list(set(rdf_triples))
    for t in rdf_print_triples:
        print(t)

    fpath = f'{OUTPUT_FOLDER}rdf_triples{timestr}.txt'
    print(f"RDF triples saved in {fpath}")
    try:
        with open(fpath,'w') as f:
            for t in rdf_print_triples:
                f.write(t)
                f.write('\n')
        f.close()
    except:
        print(f"Error while saving the rdf triples in the {OUTPUT_FOLDER} folder")
        exit()

    # print text triples
    if args.text_triples:
        print("## Text triples:")
        print('----'*5)
        for t in text_triples:
            print(t.__repr__())

    # save the debug info
    if args.save_debug:
        fpath = f'{OUTPUT_FOLDER}debug_{timestr}.ttl'
        print(f"Debug info saved in {fpath}")
        try:
            with open(fpath,'w') as f:
                f.write(debug_info)
            f.close()
        except:
            print(f"Error while saving the debug info in the {OUTPUT_FOLDER} folder")
            exit()