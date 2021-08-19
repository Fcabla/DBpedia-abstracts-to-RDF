# Scripts or helpers
This folder contains some scripts that have been used during the project and are not part of the main pipeline. Inside this folder you can find another Readme file with a description of each one.

**clause_extraction.py** contains the first approach of extracting the clauses using ClausIE, more info in the [coding week 1 blog](https://fcabla.github.io/DBpedia-abstracts-to-RDF/coding-week1)

**dependency_trees_spacy.py** contains some initiall tests in order to get familiarized with the spacy library.

**rdf2csv.py** that takes N random abstracts from a TTL file (RDF) and creates a csv file with
those n random abstracts.

**most_common_verbs.py** Script to extract the most common verbs, verbs + prepositions and complex phrasal verbs in a sample of DBpedia abstracts.

**cumsum_common_verbs_preps.py** Computes the cumulative sum of the most common verbs and prepositions, then plot it. More info in the [coding week 7 blog](https://fcabla.github.io/DBpedia-abstracts-to-RDF/coding-week7)

**build_lookup_table.py** Create the structure of the lookup table (json) verbs + prepositions -> property (dbpedia ontology). More info in the [coding week 7 blog](https://fcabla.github.io/DBpedia-abstracts-to-RDF/coding-week7)

**build_classes_lookup.py** Script to create the structure of the lookup table noun -> dbpedia class (dbpedia ontology). More info in the [coding week 8 blog](https://fcabla.github.io/DBpedia-abstracts-to-RDF/coding-week8)

