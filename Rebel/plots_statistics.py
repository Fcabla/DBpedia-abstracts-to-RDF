"""
Script to generate 2 plots based on the results of the differente configurations for REBEL and
Text2RDF.
The plots can be found under the rebel/results folder: lexicalization_strategy_rebel.svg and text2rdf_rebel.svg

Author: Fernando Casabán Blasco
"""
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

DOC_PATHS = 'Rebel/results/'

def fix_relations_format(x):
    x = x.strip('][')
    x = x[1:-1]
    x = x.split("', '")
    return x

#  1. Read all the csv files
df_text2rdf = pd.read_csv(filepath_or_buffer=DOC_PATHS+'text2rdf_triples.csv')
df_rebel = pd.read_csv(filepath_or_buffer=DOC_PATHS+'rebel_triples_rdf.csv')
df_rebel_any = pd.read_csv(filepath_or_buffer=DOC_PATHS+'rebel_triples_rdf_any.csv')
df_rebel_exact = pd.read_csv(filepath_or_buffer=DOC_PATHS+'rebel_triples_rdf_exact.csv')
df_rebel_othertypes = pd.read_csv(filepath_or_buffer=DOC_PATHS+'rebel_triples_rdf_othertypes.csv')

# 2. Fix inputs
df_text2rdf['relations'] = df_text2rdf['relations'].apply(fix_relations_format)
df_text2rdf['rdf_triples'] = df_text2rdf['rdf_triples'].apply(fix_relations_format)

df_rebel['relations'] = df_rebel['relations'].apply(fix_relations_format)
df_rebel['rdf_triples'] = df_rebel['rdf_triples'].apply(fix_relations_format)

df_rebel_any['relations'] = df_rebel_any['relations'].apply(fix_relations_format)
df_rebel_any['rdf_triples'] = df_rebel_any['rdf_triples'].apply(fix_relations_format)

df_rebel_exact['relations'] = df_rebel_exact['relations'].apply(fix_relations_format)
df_rebel_exact['rdf_triples'] = df_rebel_exact['rdf_triples'].apply(fix_relations_format)

df_rebel_othertypes['relations'] = df_rebel_othertypes['relations'].apply(fix_relations_format)
df_rebel_othertypes['rdf_triples'] = df_rebel_othertypes['rdf_triples'].apply(fix_relations_format)

# 3. Count how many relations and rdfs in each
df_text2rdf['relations_count'] = df_text2rdf['relations'].apply(lambda x: len(x))
df_text2rdf['rdf_triples_count'] = df_text2rdf['rdf_triples'].apply(lambda x: len(x))

df_rebel['relations_count'] = df_rebel['relations'].apply(lambda x: len(x))
df_rebel['rdf_triples_count'] = df_rebel['rdf_triples'].apply(lambda x: len(x))

df_rebel_any['relations_count'] = df_rebel_any['relations'].apply(lambda x: len(x))
df_rebel_any['rdf_triples_count'] = df_rebel_any['rdf_triples'].apply(lambda x: len(x))

df_rebel_exact['relations_count'] = df_rebel_exact['relations'].apply(lambda x: len(x))
df_rebel_exact['rdf_triples_count'] = df_rebel_exact['rdf_triples'].apply(lambda x: len(x))

df_rebel_othertypes['relations_count'] = df_rebel_othertypes['relations'].apply(lambda x: len(x))
df_rebel_othertypes['rdf_triples_count'] = df_rebel_othertypes['rdf_triples'].apply(lambda x: len(x))

# 4. Plots
print(f"Text2RDF relation avg: {df_text2rdf['relations_count'].mean()}, rdf avg: {df_text2rdf['rdf_triples_count'].mean()}")
print(f"Rebel relation avg: {df_rebel['relations_count'].mean()}, rdf avg: {df_rebel['rdf_triples_count'].mean()}")
print(f"Rebel_any relation avg: {df_rebel_any['relations_count'].mean()}, rdf avg: {df_rebel_any['rdf_triples_count'].mean()}")
print(f"Rebel_exact relation avg: {df_rebel_exact['relations_count'].mean()}, rdf avg: {df_rebel_exact['rdf_triples_count'].mean()}")
print(f"Rebel_othertypes relation avg: {df_rebel_othertypes['relations_count'].mean()}, rdf avg: {df_rebel_othertypes['rdf_triples_count'].mean()}")

#       4.1 plot text2rdf against rebel custom
x = np.arange(2)
y1 = [df_text2rdf['relations_count'].mean(), df_rebel['relations_count'].mean()]
y2 = [df_text2rdf['rdf_triples_count'].mean(), df_rebel['rdf_triples_count'].mean()]
width = 0.2
  
# plot data in grouped manner of bar type
plt.bar(x-0.2, y1, width)
plt.bar(x, y2, width)
plt.xticks(x, ['Text2RDF', 'Rebel'])
plt.xlabel("Model")
plt.ylabel("AVG triplet counter")
plt.legend(["Text triples", "RDF triples"])
plt.show()

#       4.2 plot text2rdf against rebel custom
data = {'Rebel_any':(df_rebel_any['rdf_triples_count'].mean()*100)/df_rebel_any['relations_count'].mean(),
        'Rebel_exact':(df_rebel_exact['rdf_triples_count'].mean()*100)/df_rebel_exact['relations_count'].mean(),
        'Rebel_custom':(df_rebel['rdf_triples_count'].mean()*100)/df_rebel['relations_count'].mean(),
        'Rebel_othertypes':(df_rebel_othertypes['rdf_triples_count'].mean()*100)/df_rebel_othertypes['relations_count'].mean()}
names_cols = list(data.keys())
values = list(data.values())
 
# creating the bar plot
plt.bar(names_cols, values,
        width = 0.4,edgecolor ='grey')
 
plt.xlabel("Lexicalization strategy for REBEL")
plt.ylabel("% of translated triples")
plt.show()