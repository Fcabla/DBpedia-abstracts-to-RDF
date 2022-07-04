import json
import os
import spacy

DBPEDIA_LINK = "http://dbpedia.org/ontology/"
path = '../../datasets/en_properties/'
files = os.listdir(path)

lookup = {}
nlp = spacy.load("en_core_web_trf")
count = 0
for file in files:
    with open(path + file, 'r') as f:
        for line in f:
            if any(x in line for x in ["RelationalAdjective", "StateVerb", "ConsequenceVerb"]):
                split = line.split('"')
                if len(split) != 3:
                    continue
                verb = split[1]
                doc = nlp(verb)
                for token in doc:
                    verb = token.lemma_
                uri = split[2].split(',')[1]
                uri = uri[:-1] if uri[-1] == '\n' else uri
                uri = uri[:-1] if uri[-1] == ')' else uri
                if "dbpedia" in uri:
                    count = count + 1
                    uri = uri.replace("dbpedia:", DBPEDIA_LINK)
                    uri = uri.replace("<", "")
                    uri = uri.replace(">", "")
                    next_line = next(f)
                    prep = 'DEF'
                    if "PrepositionalObject" in next_line:
                        prep = next_line.split('"')[1]
                    if verb not in lookup:
                        lookup[verb] = {prep: [uri]}
                    elif prep not in lookup[verb]:
                        lookup[verb].update({prep: [uri]})
                    else:
                        lookup[verb][prep].append(uri)

print(count)
with open('new_verb_prep_property_lookup.json', 'w') as f:
    json.dump(lookup, f, indent=4)
