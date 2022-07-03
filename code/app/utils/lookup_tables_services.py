import json


def load_lexicalization_table(lex_path):
    """ Return the lexicalization table as a python dict of dics (verbs and prepositions, classes) """
    try:
        with open(lex_path) as json_file:
            lex_table = json.load(json_file)
        json_file.close()
    except:
        print(f"Error while parsing the {lex_path} file, please check if the folder file is reacheable and if the path is correct")
        return False
    return lex_table


def save_lexicalization_table(lex_path, lex_table):
    """ Save the lexicalization table in a json file """
    try:
        json_file = open(lex_path, "w")
        json.dump(lex_table, json_file, indent=4)
        json_file.close()
    except:
        print(f"Error while parsing the {lex_path} file, please check if the path is correct")
        return False
    return True


def insert_new_URI_lextable(verb, prep, URI, lex_table):
    """ Adds a new URI to a lexicalization table entry.
     Depends on whether the existing entry is a list, string or contains "UNK" """
    entry = lex_table[verb][prep]
    if type(entry) == list:  # exist several URIs
        lex_table[verb][prep].append(URI)
    else:
        if entry == "UNK":  # no URI exist
            lex_table[verb][prep] = URI
        else:  # there is only 1 URI (string)
            lex_table[verb][prep] = [entry, URI]

    return lex_table


def update_classes_lookup(class_name, class_URI, lex_table, lex_path):
    """ Adds a new URI to a lexicalization table entry.
     Depends on whether the existing entry is a list, string or contains "UNK" """
    lex_table[class_name.lower()] = class_URI
    return save_lexicalization_table(lex_path, lex_table)


def update_verb_prep_property_lookup(verb, prep, property_URI, lex_table, lex_path):
    """ Adds a new URI to a lexicalization table entry.
     Depends on whether the existing entry is a list, string or contains "UNK" """
    if verb in lex_table:
        if prep:
            prep = prep.lower()
            if prep in lex_table[verb]:  # exist verb and prep in table
                lex_table = insert_new_URI_lextable(verb, prep, property_URI, lex_table)
            else:                                   # exist verb in table but no prep
                lex_table[verb][prep] = property_URI
        else:                                       # exist verb but no prep was indicated by user
            lex_table = insert_new_URI_lextable(verb, 'DEF', property_URI, lex_table)
    else:
        if prep:                                    # neither verb nor prep exist in table
            prep = prep.lower()
            lex_table[verb] = {prep: property_URI}
        else:                                       # verb not exist in table, and no prep was indicated by user
            lex_table[verb] = {'DEF': property_URI}

    return save_lexicalization_table(lex_path, lex_table)
