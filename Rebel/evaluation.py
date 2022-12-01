import pandas as pd
from rdflib import Graph, URIRef, Literal
from rdflib.namespace import RDF
from SPARQLWrapper import SPARQLWrapper, JSON
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

PROPERTIES_DATES = ["http://www.wikidata.org/wiki/Property:P1191", "http://dbpedia.org/ontology/startDate", "http://www.wikidata.org/wiki/Property:P576", "http://dbpedia.org/ontology/birthDate", "http://dbpedia.org/ontology/deathDate", "http://dbpedia.org/ontology/publicationDate", "http://dbpedia.org/ontology/startDateTime", "http://dbpedia.org/ontology/endDateTime", ]
PROPERTIES_YEARS = ["http://www.wikidata.org/wiki/Property:P585", "http://www.wikidata.org/wiki/Property:P571"]
PROPERTIES_INTEGERS = ["http://dbpedia.org/ontology/numberOfPeopleAttending", "http://dbpedia.org/ontology/numberOfEpisodes"]

EVAL_FILE = 'Rebel/results/rebel_triples_rdf_othertypes.CSV'

def fix_relations_format(x):
    x = x.strip('][')
    x = x[1:-1]
    x = x.split("', '")
    #x = [elem.lower() for elem in x]
    return x

def eval_triples_ont_old(x, graph):
    results = []
    for elem in x:
        # Parse the triplet into RDFLib objs
        triple_elements = elem.split('|')
        subj = URIRef(triple_elements[0])
        prop = URIRef(triple_elements[1])
        if 'dbpedia.org/resource/' in triple_elements[2]:
            obj = URIRef(triple_elements[2])
        else:
            obj = Literal(triple_elements[2])

        print(subj, prop, obj)
        # Query if triple in graph
        results.append((subj, prop, obj) in graph)
        
    return results

def eval_triples_ont(x, sparql):
    results = []
    for elem in x:
        # Parse the triplet into RDFLib objs
        triple_elements = elem.split('|')
        if len(triple_elements) != 3:
            print(triple_elements)
            continue
            
        subj = triple_elements[0]
        prop = triple_elements[1]

        if 'dbpedia.org/resource/' in triple_elements[2]:
            obj = f'<{triple_elements[2]}>'
        else:
            obj = triple_elements[2]
            if prop in PROPERTIES_DATES:
                obj = f'"{obj}"^^xsd:dateTime'
            elif prop in PROPERTIES_YEARS:
                obj = f'"{obj}"^^xsd:xsd:gYear'
                #prop = f'"{prop}"^^xsd:dateTime'
            elif prop in PROPERTIES_INTEGERS:
                obj = f'"{obj}"^^xsd:xsd:int'
        
        # Query if triple in graph
        sparql.setQuery(f"""
            ASK WHERE {{
                <{subj}> <{prop}> {obj}
            }}
        """
        )
        try:
            result_query = sparql.queryAndConvert()
            results.append(result_query['boolean'])
        except:
            print('error with:')
            print(f'{subj}|{prop}|{obj}')
            results.append(False)
    return results

def eval_range_domain(x):
    counter = 0
    for elem in x: 
        pass

    """
    select ?pdomain ?prange ?tsubject ?tobject
    where {
        <http://dbpedia.org/ontology/foundationPlace> rdfs:domain ?pdomain .
        <http://dbpedia.org/ontology/foundationPlace> rdfs:range ?prange  .
        <http://dbpedia.org/resource/Cyprus> a ?tsubject  .
        <http://dbpedia.org/resource/Crete> a ?tobject.
    } LIMIT 100

    """
    return 0

def main():
    # 1. Read csv
    df = pd.read_csv(filepath_or_buffer=EVAL_FILE)
    df = df[:100]

    # 2. Fix triples format (string to list) 
    df['relations'] = df['relations'].apply(fix_relations_format)
    df['rdf_triples'] = df['rdf_triples'].apply(fix_relations_format)

    # 3. Load DBpedia graph:
    #g = Graph()
    #g.parse("https://dbpedia.org/sparql")
    #print(g)
    sparql = SPARQLWrapper("http://dbpedia.org/sparql")
    #sparql.addDefaultGraph("http://dbpedia.org")
    sparql.setReturnFormat(JSON)

    # 4. For each  abstract:
    df['eval_triples_ont'] = df['rdf_triples'].apply(eval_triples_ont, sparql = sparql)
    num_rdf_triples = sum(df['rdf_triples'].apply(lambda x: len(x)))
    num_correct_rdf_triples = sum(df['eval_triples_ont'].apply(lambda x: sum(x)))
    print(num_rdf_triples, num_correct_rdf_triples)
    for elem in df['eval_triples_ont']:
        print(sum(elem))
    #print(df['eval_triples_ont'])
    #df['eval_range_domain'] = df['rdf_triples'].apply(eval_range_domain)

if __name__ == '__main__':
    main()

"""

:Requiredfor rdfs:domain ?domain ;||
||               rdfs:range ?range .
"""