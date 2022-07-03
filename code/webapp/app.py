"""
Author: Fernando Casabán Blasco and Pablo Hernández Carrascosa
"""
import glob
import os
import time

import pandas as pd
import spacy
import coreferee
import streamlit as st
from st_aggrid import AgGrid, GridUpdateMode, GridOptionsBuilder
import utils.update_ontology as uo
import validators
from rdflib.term import URIRef

import utils.build_RDF_triples as brt
import utils.lookup_tables_services as lts
import utils.preprocess_sentences as pps
import utils.process_triples as pt
import utils.triples_extraction as te

timestr = time.strftime("%Y%m%d-%H%M%S")
SPOTLIGHT_ONLINE_API = "https://api.dbpedia-spotlight.org/en/annotate"
PROP_LEXICALIZATION_TABLE = "datasets/verb_prep_property_lookup.json"
CLA_LEXICALIZATION_TABLE = "datasets/classes_lookup.json"


def pipeline(nlp, raw_text, dbo_graph, prop_lex_table, cla_lex_table):
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
                resultado = resultado + doc[pointer:tupla[0]].text_with_ws + tupla[1]
                pointer = tupla[0] + 1
            resultado = resultado + doc[pointer:].text_with_ws
            doc = nlp(resultado)

    sentences = pps.get_sentences(doc)
    triples, n_sent_simples = te.get_all_triples(nlp, sentences)
    triples = pt.split_amod_conjunctions_subj(nlp, triples)
    triples = pt.split_amod_conjunctions_obj(nlp, triples)

    try:
        term_URI_dict, term_types_dict = brt.get_annotated_text_dict(raw_text, service_url=SPOTLIGHT_ONLINE_API)
    except:
        return [], []

    rdf_triples = brt.replace_text_URI(triples, term_URI_dict, term_types_dict, prop_lex_table, cla_lex_table, dbo_graph)
    return triples, rdf_triples


def print_debug(triples):
    """ Print the final result: Original sentence, text triples and rdf triples"""
    if triples:
        for t in triples:
            st.write(t.sent + '\n')
            st.write('--> ' + t.__repr__() + '\n')
            st.write('--> ' + t.get_rdf_triple() + '\n')
            st.write('----')


def get_only_triples_URIs(rdf_triples):
    """ Keep just the triples that are entirely made of URIRef. """
    return [t for t in rdf_triples if isinstance(t.pred_rdf, URIRef) and isinstance(t.objct_rdf, URIRef)]


@st.cache(allow_output_mutation=True)
def init():
    """ Function to load all the external components. """
    # Load dependency model and add coreferee support
    nlp = spacy.load("en_core_web_trf")
    nlp.add_pipe('coreferee')
    # Load datastructures
    prop_lex_table = lts.load_lexicalization_table(PROP_LEXICALIZATION_TABLE)
    cla_lex_table = lts.load_lexicalization_table(CLA_LEXICALIZATION_TABLE)
    dbo_graph = brt.load_dbo_graph(DBPEDIA_ONTOLOGY)

    return nlp, prop_lex_table, cla_lex_table, dbo_graph


def clear_form():
    st.session_state["inputtext"] = ""


def insert_class_table(class_name, class_uri):
    if not validators.url(class_uri):
        st.error(f'The URI {class_uri} is not valid')
        return
    class_name = class_name.lower()
    res, msg = lts.insert_classes_lookup(class_name, class_uri, cla_lex_table, CLA_LEXICALIZATION_TABLE)
    if res:
        st.success(f'The class {class_name} with URI {class_uri} has been created')
        st.session_state.cla_lex_table[class_name] = class_uri
        st.session_state.class_tbl.loc[-1] = [class_name, class_uri]
        st.session_state.class_tbl.index = st.session_state.class_tbl.index + 1
        st.session_state.class_tbl.sort_index(inplace=True)
    else:
        st.error(msg)


def update_class_table(new_cla_lex_table):
    diff = set(new_cla_lex_table.items()) ^ set(cla_lex_table.items())
    for value in diff:
        if not validators.url(value[1]):
            st.error(f'The URI {value[1]} is not valid')
            return
    if lts.update_classes_lookup(new_cla_lex_table, CLA_LEXICALIZATION_TABLE):
        st.success('Class has been updated')
        st.session_state.cla_lex_table = new_cla_lex_table
    else:
        st.error('Class could not be updated')


def delete_class_table(rows_selected):
    classes = [row['class_name'] for row in rows_selected]
    if lts.delete_classes_lookup(classes, cla_lex_table, CLA_LEXICALIZATION_TABLE):
        st.success(f'The classes {classes} were deleted')
        st.session_state.class_tbl = st.session_state.class_tbl[~st.session_state.class_tbl.class_name.isin(classes)]
    else:
        st.error('Class could not be deleted')


def insert_prop_table(verb, prep, prop_uri):
    if not validators.url(prop_uri):
        st.error(f'The URI {prop_uri} is not valid')
        return
    verb = verb.lower()
    prep = prep.lower()
    res, prop_lex_path, msg, new_row = lts.insert_props_lookup(verb, prep, prop_uri, prop_lex_table, PROP_LEXICALIZATION_TABLE)
    if res:
        st.success(f'The property ({verb}, {prep}) with URI {prop_uri} has been created')
        st.session_state.prop_lex_table = prop_lex_table
        if new_row:
            st.session_state.prop_tbl.loc[-1] = [verb.lower(), prep.lower(), prop_uri]
            st.session_state.prop_tbl.index = st.session_state.prop_tbl.index + 1
            st.session_state.prop_tbl.sort_index(inplace=True)
        else:
            if not prep:
                prep = 'DEF'
            df = st.session_state.prop_tbl
            previous_uri = df[(df['verb'] == verb) & (df['prep'] == prep)]
            index = previous_uri.index[0]
            new_uri_list = list(previous_uri['uri'])
            new_uri_list.append(prop_uri)
            new_uri_list = ', '.join(new_uri_list)
            df.at[index, 'uri'] = new_uri_list
    else:
        st.error(msg)


def update_prop_table(new_prop_lex_table):
    if lts.update_props_lookup(new_prop_lex_table, PROP_LEXICALIZATION_TABLE):
        st.success('Property has been updated')
        st.session_state.prop_lex_table = new_prop_lex_table
    else:
        st.error('Property could not be updated')


def delete_prop_table(rows_selected):
    props = [(row['verb'], row['prep']) for row in rows_selected]
    if lts.delete_props_lookup(props, prop_lex_table, PROP_LEXICALIZATION_TABLE):
        st.success(f'The properties {props} were deleted')
        for verb, prep in props:
            st.session_state.prop_tbl = st.session_state.prop_tbl.drop(
                st.session_state.prop_tbl[
                    (st.session_state.prop_tbl['verb'] == verb) & (st.session_state.prop_tbl['prep'] == prep)].index)
    else:
        st.error('Property could not be deleted')


def create_grid_table(data):
    gd = GridOptionsBuilder.from_dataframe(data)
    gd.configure_pagination(enabled=True, paginationAutoPageSize=False, paginationPageSize=20)
    gd.configure_default_column(editable=True, groupable=True, min_column_width=5)
    gd.configure_selection(selection_mode='multiple', use_checkbox=True)
    grid_options = gd.build()

    return AgGrid(data, gridOptions=grid_options, height=500, theme='material',
                  update_mode=GridUpdateMode.SELECTION_CHANGED | GridUpdateMode.VALUE_CHANGED |
                              GridUpdateMode.FILTERING_CHANGED | GridUpdateMode.SORTING_CHANGED |
                              GridUpdateMode.MODEL_CHANGED | GridUpdateMode.MANUAL,
                  fit_columns_on_grid_load=True, reload_data=True)


if __name__ == "__main__":
    st.set_page_config(page_title='Text to RDF', layout='wide')
    local_ontology_path = 'datasets/'
    local_ontology_files = glob.glob(f'{local_ontology_path}*.owl')
    names = [os.path.basename(x) for x in local_ontology_files]
    namesSorted = sorted(names, reverse=True)
    DBPEDIA_ONTOLOGY = local_ontology_path + namesSorted[0]

    nlp, prop_lex_table, cla_lex_table, dbo_graph = init()

    # Create a page dropdown list at sidebar
    page = st.sidebar.selectbox("Choose your task", ["Text to RDF", "Update look up tables"])
    if page == "Text to RDF" or not page:

        st.header('DBpedia abstracts to RDF')
        st.write('This app translates any kind of text into RDF!')

        with st.form('my_form'):
            st.subheader('User input parameters')
            raw_text = st.text_area('Insert abstract or any other kind of text', key='inputtext', height=200,
                                    help='Insert abstract or any other kind of text in order to generate RDF based on the input')
            show_text_triples = st.checkbox('Show text triples',
                                            help='Print the text tripels from the sentences. This is useful to understand how the pipeline processed the input')
            print_debg = st.checkbox('Print debug information',
                                     help='Print the text triples and RDF triples extracted for every sentence')

            col1, col2, _, _, _, _, _, _ = st.columns(8)
            submitted = col1.form_submit_button("Submit")
            col2.form_submit_button("Clear text", on_click=clear_form)

        if submitted:
            # primitive user input check
            if len(raw_text) < 20:
                st.write("Invalid input text, try something bigger")
            else:
                with st.spinner('Processing text...'):
                    text_triples, rdf_triples = pipeline(nlp, raw_text, dbo_graph, prop_lex_table, cla_lex_table)

                if not rdf_triples:
                    st.warning('No RDF triples where obtained')
                    st.stop()
                st.success('Done!')

                # save triples in a graph and returns the graph serialized (ttl format)
                graph, graph_serialized = brt.build_result_graph(rdf_triples)

                # RDF triples
                st.subheader("RDF triples:")
                # read triples from rdf graph
                for s, p, o in graph.triples((None, None, None)):
                    st.write(s, ' | ', p, ' | ', o)

                # download_ttl(graph_serialized)
                st.download_button(label='Download ".ttl" file', data=graph_serialized, file_name='graph.ttl', mime='file/ttl')

                # Text triples
                if show_text_triples:
                    st.write('----')
                    st.subheader("Text triples:")
                    for t in text_triples:
                        st.write(t.__repr__())

                # Debug info
                if print_debg:
                    st.write('----')
                    st.subheader("Debug:")
                    print_debug(rdf_triples)

    elif page == "Update look up tables":
        st.header('Lexicalization tables')
        if update_ontology := st.sidebar.button('Update DBpedia ontology', help='Download latest DBpedia ontology in format owl'):
            with st.spinner('This task can take a while. Please wait...'):
                download_state = uo.update_ontology_file()
            if not download_state[0]:
                st.sidebar.error(download_state[1])
            else:
                st.sidebar.success(download_state[1])
                st.sidebar.success('Please, re-run app to load changes')

        col1, _, _, _, _ = st.columns(5)
        with col1:
            option = st.selectbox('', options=('Classes', 'Properties'))

        if option == 'Classes':
            if "class_tbl" not in st.session_state:
                df_classes = pd.DataFrame.from_dict(cla_lex_table, orient="index", columns=["URI"]).reset_index()
                df_classes.rename(columns={'index': 'class_name'}, inplace=True)
                st.session_state.class_tbl = df_classes
                st.session_state.cla_lex_table = cla_lex_table

            grid_class_table = create_grid_table(st.session_state.class_tbl)

            selection_list = grid_class_table["selected_rows"]
            st.button('Delete', on_click=delete_class_table, args=(selection_list,), disabled=selection_list == [])

            dict_df = dict(zip(grid_class_table['data'].class_name, grid_class_table['data'].URI))
            if dict_df != st.session_state.cla_lex_table:
                update_class_table(dict_df)

            _, col_form, _ = st.columns(3)
            with col_form:
                with st.form("insert_class_form"):
                    st.subheader('New entry')
                    class_name = st.text_input('Enter class name:', key="name")
                    class_URI = st.text_input('Enter URI:', key="URI")
                    if submitted_insert_class_form := st.form_submit_button("Submit"):
                        insert_class_table(class_name, class_URI)

        elif option == 'Properties':
            if "prop_tbl" not in st.session_state:
                df_prop = pd.DataFrame(columns=['verb', 'prep', 'URI'])
                for verb in prop_lex_table.keys():
                    for prep, uri in prop_lex_table[verb].items():
                        df_prop = pd.concat([df_prop, pd.DataFrame([[verb, prep, uri]], columns=df_prop.columns)], ignore_index=True)
                df_prop['URI'] = [', '.join(map(str, l)) if isinstance(l, list) else l for l in df_prop['URI']]
                st.session_state.prop_tbl = df_prop
                st.session_state.prop_lex_table = prop_lex_table

            grid_prop_table = create_grid_table(st.session_state.prop_tbl)
            selection_list = grid_prop_table["selected_rows"]
            st.button('Delete', on_click=delete_prop_table, args=(selection_list,), disabled=selection_list == [])

            df_grid = st.session_state.prop_tbl
            verb_list = sorted(set(df_grid.verb))
            dict_df = {}
            for verb in verb_list:
                uris = []
                for uri in df_grid[df_grid['verb'] == verb]['URI']:
                    uri_list = uri.split(', ')
                    if len(uri_list) > 1:
                        uris.append(uri_list)
                    else:
                        uris.append(uri)
                dict_df[verb] = dict(zip(df_grid[df_grid['verb'] == verb]['prep'], uris))

            if dict_df != st.session_state.prop_lex_table:
                update_prop_table(dict_df)

            _, col_form, _ = st.columns(3)
            with col_form:
                with st.form("insert_prop_form"):
                    st.subheader('New entry')
                    verb = st.text_input('Enter verb (in infinitive form):', key="verb")
                    prep = st.text_input('Enter preposition (if necessary):', key="prep")
                    prop_uri = st.text_input('Enter URI:', key="pURI")
                    if submitted_insert_prop_form := st.form_submit_button("Submit"):
                        insert_prop_table(verb, prep, prop_uri)
