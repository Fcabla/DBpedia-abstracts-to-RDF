from rdflib.term import URIRef
import streamlit as st
import pandas as pd
import base64
import time

import utils.preprocess_sentences as pps
import utils.triples_extraction as te
import utils.process_triples as pt
import utils.build_RDF_triples as brt

import spacy
import coreferee

timestr = time.strftime("%Y%m%d-%H%M%S")

banned_subjects = ["he", "she", "it", "his", "hers"]
SPOTLIGHT_LOCAL_URL = "http://localhost:2222/rest/annotate/"
SPOTLIGHT_ONLINE_API = "https://api.dbpedia-spotlight.org/en/annotate"
MODIFIERS = ["compound", "amod", "nummod", "nmod", "advmod", "npadvmod"]
USE_COMPLEX_SENTENCES = False
PROP_LEXICALIZATION_TABLE = "datasets/verb_prep_property_lookup.json"
CLA_LEXICALIZATION_TABLE = "datasets/classes_lookup.json"
DBPEDIA_ONTOLOGY = "datasets/dbo_ontology_2021.08.06.owl"
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

def download_ttl(g):
    """ Build the string containing the download link of the RDF graph. """
    b64 = base64.b64encode(g).decode()
    filname = f"generated_graph_{timestr}.ttl"
    st.markdown(" #### Donwload file ####")
    href = f'<a href="data:file/ttl;base64,{b64}" download="{filname}"> Click me !!</a>'
    st.markdown(href, unsafe_allow_html=True)

def get_only_triples_URIs(rdf_triples):
    """ Keep just the triples that are entirely made of URIRef. """
    new_triples = []
    for t in rdf_triples:
        if isinstance(t.pred_rdf, URIRef) and isinstance(t.objct_rdf, URIRef):
            new_triples.append(t)
    return new_triples

@st.cache(allow_output_mutation=True)
def init():
    """ Function to load all the external components. It is supposed to run just once. """
    # Load dependency model and add coreferee support
    nlp = spacy.load("en_core_web_trf")
    nlp.add_pipe('coreferee')
    print("houlas")
    # Load datastructures
    prop_lex_table = brt.load_lexicalization_table(PROP_LEXICALIZATION_TABLE)
    cla_lex_table = brt.load_lexicalization_table(CLA_LEXICALIZATION_TABLE)
    dbo_graph = brt.load_dbo_graph(DBPEDIA_ONTOLOGY)

    return nlp, prop_lex_table, cla_lex_table, dbo_graph

if __name__ == "__main__":
    nlp, prop_lex_table, cla_lex_table, dbo_graph = init()

    st.title('DBpedia abstracts to RDF')
    st.write('This app translates any kind of text into RDF!')

    form = st.form("my_form")
    form.header('User input parameters')
    raw_text = form.text_area('Insert abstract or any other kind of text', 
                            help = 'Insert abstract or any other kind of text in order to generate RDF based on the input',
                            height=400)
    use_complex_sents = form.checkbox('Use all the sentences',
                            help='Use all the sentences of the abstract or just use the simplest senteces (it is recommended to leave the checkbox unchecked)')
    show_text_triples = form.checkbox('Show the simplified sentences',
                            help='Print the simplified sentences from the triples have been generated. This is useful to understand how the pipeline processed the input')
    retrieve_only_URIs = form.checkbox('Get only triples with no literals',
                            help='Discard all the triples containing a literal in them. This happens when the pipeline is unable to find any lexicalization to either predicate or object')
    print_debg = form.checkbox('Print debug information', help = 'Print the text triples and RDF triples extracted for every sentence')
    submitted = form.form_submit_button("Submit")

    if submitted:
        # primitive user input check
        if len(raw_text) < 20:
            st.write("Invalid input text, try something bigger")
        else:
            text_triples, rdf_triples = pipeline(nlp, raw_text, dbo_graph ,prop_lex_table, cla_lex_table, use_complex_sents)
            debug_info = print_debug(rdf_triples)
            if retrieve_only_URIs:
                rdf_triples = get_only_triples_URIs(rdf_triples)
            g = brt.build_result_graph(rdf_triples)
            download_ttl(g)

            # Printing:
            # RDF triples
            st.write("## RDF triples:")
            st.write('----')
            rdf_triples = [t.get_rdf_triple() for t in rdf_triples]
            rdf_triples = [t.__repr__() for t in rdf_triples]
            rdf_print_triples = list(set(rdf_triples))
            for t in rdf_print_triples:
                st.write(t)

            # Text triples
            if show_text_triples:
                st.write("## Text triples:")
                st.write('----')
                for t in text_triples:
                    st.write(t.__repr__())
            
            # Debug info
            if print_debg:
                st.write("## Debug:")
                st.write("The abstract sentence will be shown in bold and then the text triplet and RDF triplet that have been extracted.")
                st.write(debug_info)