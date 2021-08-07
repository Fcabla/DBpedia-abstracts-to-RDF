"""
Script to create the structure of the lookup table verbs + prepositions -> property (dbpedia ontology)
The idea is to take the first N most relevant prepositions and the first N most relevant verbs and combine them.
Adding also UNK to the unknown values and DEF to the default verb (no preposition or not found)
"""

VERBS_FILE_PATH = "results/stats/complex_sentences_common_verbs.json"
PREPOSITIONS_FILE_PATH = "results/stats/complex_sentences_common_prep.json"
UNKOWN_VALUE = "UNK"
DEFAULT_VERB = "DEF"
NVERBS = 100
NPREPS = 13
OUTPUT_FILE = "results/verb_prep_property_lookup.json"
import json
from collections import Counter

def main():
    with open(PREPOSITIONS_FILE_PATH) as prep_file, open(VERBS_FILE_PATH) as verb_file:
        # Read ordered frequency dicts (prepostions and verbs)
        verb_dict = json.load(verb_file)
        prep_dict = json.load(prep_file)

        # Select the N most common and append DEFAULT to prepositions
        verbs = list(verb_dict)[:NVERBS]
        prepositions = list(prep_dict)[:NPREPS]
        prepositions.append(DEFAULT_VERB)

    lookup = {}
    for verb in verbs:
        lookup[verb] = {prep:UNKOWN_VALUE for prep in prepositions}
    save_file = open(OUTPUT_FILE, "w")
    json.dump(lookup, save_file, indent=4)
    save_file.close()



if __name__ == "__main__":
    main()