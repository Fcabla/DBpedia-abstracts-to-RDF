"""
Author: Fernando Casabán Blasco and Pablo Hernández Carrascosa
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

    parser = argparse.ArgumentParser(description='Text to RDF parser')

    parser.add_argument('--input_text', help='Insert abstract or any other kind of text in order to generate RDF based on the input' , required=True)
    parser.add_argument('--text_triples', help='Print the simplified sentences from the triples have been generated. This is useful to understand how the pipeline processed the input', action="store_true")
    parser.add_argument('--save_debug', help='Print the text triples and RDF triples extracted for every sentence', action="store_true")
    args = parser.parse_args()

    tracking_file_name = "log_files/tracking.txt"
    if os.path.exists(tracking_file_name):
        os.remove(tracking_file_name)

    if EVALUATION:
        tracking_file_name = "log_files/literals_log.txt"
        if os.path.exists(tracking_file_name):
            os.remove(tracking_file_name)
        n_abstracts = 0
        n_sent_spacy = 0
        n_sent_simple = 0
        n_text_triples = 0
        n_RDF_triples = 0

    try:
        with open(args.input_text, encoding='utf8') as f:
            text_triples_all = []
            rdf_triples_all = []
            for line in f.readlines():
                raw_text = raw_text.replace('\n', '')
                tracking_log(raw_text, level=0)  # tracking
                text_triples, rdf_triples, nsent_spacy, nsent_simples = pipeline(nlp, raw_text, dbo_graph, prop_lex_table, cla_lex_table)
                tracking_log(text_triples, level=4)  # tracking
                if rdf_triples:
                    text_triples_all.extend(rdf_triples)

                # print/save rdf triples
                print("## RDF triples:")
                print('----'*5)
                rdf_triples = [t.get_rdf_triple() for t in rdf_triples]
                rdf_triples = [t.__repr__() for t in rdf_triples]
                rdf_print_triples = list(set(rdf_triples))
                if EVALUATION:
                    n_abstracts = n_abstracts + 1
                    n_sent_spacy = n_sent_spacy + nsent_spacy
                    n_sent_simple = n_sent_simple + nsent_simples
                    n_text_triples = n_text_triples + len(text_triples)
                    n_RDF_triples = n_RDF_triples + len(rdf_print_triples)
                    n_duplicadas = n_duplicadas + (len(rdf_triples) - len(rdf_print_triples))
                for t in rdf_print_triples:
                    print(t)
                    rdf_triples_all.append(t)
                tracking_log(rdf_print_triples, level=5)  # tracking

            # save the graph
            brt.build_save_result_graph(text_triples_all, f'{OUTPUT_FOLDER}graph_{timestr}.ttl')

            fpath = f'{OUTPUT_FOLDER}rdf_triples{timestr}.txt'
            print(f"RDF triples saved in {fpath}")
            try:
                with open(fpath, 'w', encoding='utf8') as f:
                    for t in rdf_triples_all:
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
                for t in text_triples_all:
                    print(t.__repr__())

            # save the debug info
            if args.save_debug:
                debug_info = print_debug(text_triples_all)
                fpath = f'{OUTPUT_FOLDER}debug_{timestr}.txt'
                print(f"Debug info saved in {fpath}")
                try:
                    with open(fpath, 'w', encoding='utf8') as f:
                        f.write(debug_info)
                    f.close()
                except:
                    print(f"Error while saving the debug info in the {OUTPUT_FOLDER} folder")
                    exit()

        if EVALUATION:
            print(n_abstracts, 'abstracts analizados')
            print(n_sent_spacy, 'sentencias identificadas por Spacy')
            print(n_sent_simple, 'sentencias simples analizadas')
            print(n_text_triples, 'tripletas de texto generadas')
            print(n_RDF_triples, 'tripletas RDF generadas')
            print(n_duplicadas, 'tripletas RDF duplicadas')

    except IOError:
        print(f"Error while reading {fpath} (input text)")
        exit()
