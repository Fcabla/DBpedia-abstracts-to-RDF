"""
Script to create the structure of the lookup table noun -> dbpedia class (dbpedia ontology)
"""

CLASSES_FILE_PATH = "datasets/dbo_classes.txt"
CLASS_PREFIX = "http://dbpedia.org/ontology/"
OUTPUT_FILE = "datasets/classes_lookup.json"
import json
import re

def format_string(text):
    """ Function to format strings with uppercases and no spaces IceHockeyPlayer -> ice hockey player """
    result = ""
    for letter in text:
        if letter.isupper():
            result += " "
        result += letter
    return result[1:].lower()

def main():
    with open(CLASSES_FILE_PATH) as cfile:
        # Read all the classes
        dbo_classes = cfile.readlines()
    dbo_classes = [c.replace("\n","") for c in dbo_classes]
    lookup = {}
    for c in dbo_classes:
        key = c.replace(CLASS_PREFIX,"",1)
        key = format_string(key)
        lookup[key] = c
    save_file = open(OUTPUT_FILE, "w")
    json.dump(lookup, save_file, indent=4)
    save_file.close()



if __name__ == "__main__":
    main()