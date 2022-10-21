"""
Author: Fernando Casabán Blasco and Pablo Hernández Carrascosa
Script to run the tool with several text files at the same time. Used to evaluate the tool.
"""

import argparse
import glob
import os
import time

import spacy
import coreferee
from rdflib.term import URIRef

import utils.build_RDF_triples as brt
import utils.preprocess_sentences as pps
import utils.process_triples as pt
import utils.triples_extraction as te
import utils.lookup_tables_services as lts
from utils.log_generator import tracking_log
import pandas as pd
import tqdm

timestr = time.strftime("%Y%m%d-%H%M%S")

EVALUATION = False
PROP_LEXICALIZATION_TABLE = "datasets/verb_prep_property_lookup.json"
CLA_LEXICALIZATION_TABLE = "datasets/classes_lookup.json"
OUTPUT_FOLDER = "code/app/output/"
SPOTLIGHT_ONLINE_API = "https://api.dbpedia-spotlight.org/en/annotate"
SPOTLIGHT_LOCAL_URL = "http://localhost:2222/rest/annotate/"


def pipeline(nlp, raw_text, dbo_graph ,prop_lex_table, cla_lex_table):
    raw_text = pps.clean_text(raw_text)
    doc = nlp(raw_text)
    # correferences resolution
    if doc._.coref_chains:
        rules_analyzer = nlp.get_pipe('coreferee').annotator.rules_analyzer
        interchange_tokens_pos = []  # list of tuples (pos.i, mention.text)
        for token in doc:
            if bool(doc._.coref_chains.resolve(token)):
                # there is a coreference
                mention_head = doc._.coref_chains.resolve(token)  # get the mention
                if full_mention := rules_analyzer.get_propn_subtree(doc[mention_head[0].i]):
                    mention_text = ''.join([token.text_with_ws for token in full_mention])
                    interchange_tokens_pos.append((token.i, mention_text))
                else:
                    interchange_tokens_pos.append((token.i, doc[mention_head[0].i].text))

        if interchange_tokens_pos:
            resultado = ''
            pointer = 0
            for tupla in interchange_tokens_pos:
                resultado = resultado + doc[pointer:tupla[0]].text_with_ws + tupla[1] + ' '
                pointer = tupla[0] + 1
            resultado = resultado + doc[pointer:].text_with_ws

            doc = nlp(resultado)
        tracking_log(doc, level=1)  # tracking

    sentences = pps.get_sentences(doc)
    n_sent_spacy = len(sentences)  # evaluation
    tracking_log(sentences, level=2)  # tracking

    triples, n_sent_simples = te.get_all_triples(nlp, sentences)
    triples = pt.split_amod_conjunctions_subj(nlp, triples)
    triples = pt.split_amod_conjunctions_obj(nlp, triples)

    try:
        term_URI_dict, term_types_dict = brt.get_annotated_text_dict(raw_text, service_url=SPOTLIGHT_LOCAL_URL)
    except:
        return [], [], n_sent_spacy, n_sent_simples
    rdf_triples = brt.replace_text_URI(triples, term_URI_dict, term_types_dict, prop_lex_table, cla_lex_table, dbo_graph)
    return triples, rdf_triples, n_sent_spacy, n_sent_simples


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
    return [t for t in rdf_triples if isinstance(t.pred_rdf, URIRef) and isinstance(t.objct_rdf, URIRef)]


def init():
    """ Function to load all the external components. It is supposed to run just once. """
    # Load dependency model and add coreferee support
    nlp = spacy.load("en_core_web_trf")
    nlp.add_pipe('coreferee')
    # Load datastructures
    prop_lex_table = lts.load_lexicalization_table(PROP_LEXICALIZATION_TABLE)
    cla_lex_table = lts.load_lexicalization_table(CLA_LEXICALIZATION_TABLE)
    dbo_graph = brt.load_dbo_graph(DBPEDIA_ONTOLOGY)

    return nlp, prop_lex_table, cla_lex_table, dbo_graph


if __name__ == "__main__":
    local_ontology_path = 'datasets/'
    local_ontology_files = glob.glob(f'{local_ontology_path}*.owl')
    names = [os.path.basename(x) for x in local_ontology_files]
    namesSorted = sorted(names, reverse=True)
    DBPEDIA_ONTOLOGY = local_ontology_path + namesSorted[0]

    nlp, prop_lex_table, cla_lex_table, dbo_graph = init()

    print('DBpedia abstracts to RDF')
    print('This app translates any kind of text into RDF!')

    # Read pandas
    from_index = 3000
    to_index = 10000
    df = pd.read_csv('datasets/long-abstracts-sample.csv')
    df = df.to_dict(orient='records')
    try:
        df = df[from_index:to_index]
    except:
        print("Index errors")
        exit()
    for elem in tqdm.tqdm(df):
        text_triples_all = []
        rdf_triples_all = []
        raw_text = elem['abstract'].replace('\n', '')
        try:
            text_triples, rdf_triples, nsent_spacy, nsent_simples = pipeline(nlp, raw_text, dbo_graph, prop_lex_table, cla_lex_table)
            if rdf_triples:
                    text_triples_all.extend(rdf_triples)
            rdf_triples = [t.get_rdf_triple() for t in rdf_triples]
            rdf_triples = [t.__repr__() for t in rdf_triples]
            rdf_print_triples = list(set(rdf_triples))
            elem['nsent_spacy'] = nsent_spacy
            elem['nsent_simples'] = nsent_simples
            elem['relations'] = text_triples
            elem['rdf_triples'] = rdf_print_triples
        except:
            print('error')
            elem['nsent_spacy'] = -1
            elem['nsent_simples'] = -1
            elem['relations'] = ['None']
            elem['rdf_triples'] = ['None']

    df = pd.DataFrame.from_records(df)
    df.to_csv(f'code/app/output/text2rdf_triples{from_index}_{to_index}.csv')
        #{'individual': 'http://dbpedia.org/resource/Lefkogeia', 'abstract': 'Lefkogeia (Greek: Λευκόγεια) is a village in the municipal unit of Foinikas, Rethymno regional unit, Crete, Greece. The village has 289 inhabitants.', 'test': 'Lefko'}
