import json


def load_lexicalization_table(lex_path):
    """ Return the lexicalization table as a python dict of dics (verbs and prepositions, classes) """
    try:
        with open(lex_path) as json_file:
            lex_table = json.load(json_file)
    except:
        print(
            f"Error while parsing the {lex_path} file, please check if the folder file is reacheable and if the path is correct")
        return False
    return lex_table


def save_lexicalization_table(lex_table, lex_path):
    """ Save the lexicalization table in a json file """
    try:
        with open(lex_path, "w") as json_file:
            json.dump(lex_table, json_file, indent=4)
    except:
        print(f"Error while parsing the {lex_path} file, please check if the path is correct")
        return False
    return True


def insert_classes_lookup(class_name, class_uri, cla_lex_table, cla_lex_path):
    if class_name not in cla_lex_table:
        cla_lex_table[class_name] = class_uri
        return save_lexicalization_table(cla_lex_table, cla_lex_path), ''
    else:
        return False, 'Error, class name already exists'


def update_classes_lookup(cla_lex_table, cla_lex_path):
    return save_lexicalization_table(cla_lex_table, cla_lex_path)


def delete_classes_lookup(classes_list, cla_lex_table, cla_lex_path):
    for row in classes_list:
        if row not in cla_lex_table:
            return False
    for row in classes_list:
        del cla_lex_table[row]
    return save_lexicalization_table(cla_lex_table, cla_lex_path)


def insert_props_lookup(verb, prep, prop_uri, prop_lex_table, prop_lex_path):
    new_row = True
    if verb in prop_lex_table:
        if prep:
            if prep in prop_lex_table[verb]:
                prop_lex_table = insert_new_uri_lextable(verb, prep, prop_uri, prop_lex_table)
                new_row = False
            else:
                prop_lex_table[verb][prep] = prop_uri
        else:
            if 'DEF' in prop_lex_table[verb]:
                new_row = False
            prop_lex_table = insert_new_uri_lextable(verb, 'DEF', prop_uri, prop_lex_table)
    elif prep:
        prop_lex_table[verb][prep] = prop_uri
    else:
        prop_lex_table[verb]['DEF'] = prop_uri
    return save_lexicalization_table(prop_lex_table, prop_lex_path), prop_lex_table, '', new_row


def update_props_lookup(prop_lex_table, prop_lex_path):
    return save_lexicalization_table(prop_lex_table, prop_lex_path)


def delete_props_lookup(props_list, prop_lex_table, prop_lex_path):
    for row in props_list:
        verb, prep = row
        if verb not in prop_lex_table or prep not in prop_lex_table[verb]:
            return False
    for row in props_list:
        verb, prep = row
        del prop_lex_table[verb][prep]
    return save_lexicalization_table(prop_lex_table, prop_lex_path)


def insert_new_uri_lextable(verb, prep, prop_uri, prop_lex_table):
    """ Adds a new URI to a lexicalization table entry.
     Depends on whether the existing entry is a list, string or contains "UNK" """
    if 'DEF' in prop_lex_table[verb]:
        entry = prop_lex_table[verb][prep]
        if type(entry) == list and prop_uri not in prop_lex_table[verb][prep]:  # exist several URIs
            prop_lex_table[verb][prep].append(prop_uri)
        else:
            if entry == "UNK":  # no URI exist
                prop_lex_table[verb][prep] = prop_uri
            else:  # there is only 1 URI (string)
                if prop_uri not in prop_lex_table[verb][prep]:
                    prop_lex_table[verb][prep] = [entry, prop_uri]
    else:
        prop_lex_table[verb]['DEF'] = prop_uri
    return prop_lex_table
