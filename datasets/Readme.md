## Datasets
This file contains the datasets or files that have been used as data source during the whole project.

**examples.csv** is a csv file with 12 DBpedia abstracts.

**short-abstracts_lang=en.ttl** dataset with short abstracts in English, not used so far. It is not on github as it exceeds the maximum file size, can be donwloaded [here](https://databus.dbpedia.org/vehnem/text/short-abstracts/2021.05.01)

**long-abstracts_lang=en.ttl** dataset with long abstracts in English, is the dataset that has been mainly used to test the application. It is not on github as it exceeds the maximum file size, can be donwloaded [here](https://databus.dbpedia.org/vehnem/text/long-abstracts/2021.05.01)

**temp.ttl** intermediate file for the creation of the long-abstracts-sample file. The process consists of selecting N random abstracts from the long-abstracts.ttl dataset and saving them in this file. It is then transformed to the long-abstracts-sample.csv file.

**long-abstracts-sample.csv** sample of the long-abstracts.ttl dataset in csv format. More information in the [coding week 6 blog post](https://fcabla.github.io/DBpedia-abstracts-to-RDF/coding-week6)

**dbo_ontology_2021.08.06.owl** the latest DBpedia ontology (2021-08-06), used to extract a list of ObjectProperties, Classes and query range and domains of certain properties.

**dbo_object_properties.txt** is a list of the ObjectProperties found in the DBpedia ontology (dbo_ontology_2021.08.06.owl)

**dbo_classes.txt** is a list of the classes found in the DBpedia ontology (dbo_ontology_2021.08.06.owl)

**verb_prep_property_lookup.json** lookup table to translate verbs+preposition into DBpedia ObjectProperties. More information in the [coding week 7 blog post](https://fcabla.github.io/DBpedia-abstracts-to-RDF/coding-week6)

**classes_lookup.json** lookup table to translate nouns into DBpedia Classes (when the verb to be is found as the predicate). More information in the [coding week 8 blog post](https://fcabla.github.io/DBpedia-abstracts-to-RDF/coding-week8)

