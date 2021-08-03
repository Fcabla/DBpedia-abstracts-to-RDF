"""
A script that takes N random abstracts from a TTL file (RDF) and creates a csv file with
those n random abstracts.
"""
from rdflib import Graph
import pandas as pd
import os

N = 10000
INPUT_FILE = "datasets/long-abstracts_lang=en.ttl"
INTERMEDIATE_FILE = "datasets/temp.ttl"
OUTPUT_FILE = "datasets/long-abstracts-sample.csv"

def get_random_abstracts():
    """ Randomly selects N abstracts from the INPUT_FILE (3.2 Gb) and stores it in an intermediate file """
    os.system(f"shuf -n {N} {INPUT_FILE} > {INTERMEDIATE_FILE}")

def get_graph():
    """ Returns a rdflib graph with the sampled ttl file """
    g = Graph()
    g.parse(INTERMEDIATE_FILE, format='ttl')
    print(f"Graph of length {len(g)}")
    return g

def create_df_graph(g):
    """ Returns a pandas dataframe from the collected data of the RDF graph """
    data = []
    for s, p, o in g:
        # the property (p) is always the same 
        data.append([s,o])
    df = pd.DataFrame(data, columns=['individual', 'abstract'])
    #df = df.drop('property', 1)
    return df

def main():
    get_random_abstracts()
    g = get_graph()
    df = create_df_graph(g)
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"Created a csv file {OUTPUT_FILE} with {N} random dbpedia abstracts")

if __name__ == "__main__":
    main()