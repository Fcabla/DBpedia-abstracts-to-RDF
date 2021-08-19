# Translating text into RDF 2
In this eighth week we have dedicated ourselves to build the necessary functions to correctly convert text triples into RDF triples. In addition, we have filled in the lexicalization table a bit more and fixed some bugs.

## Lexicalization table
During this week we have continued to complete the lexicalization table to convert verbs + prepositions into properties of the dbpedia ontology. So far there are 40 lexicalizations, some of them with multiple options. For example, the verb `to be in` has as possible lexicalizations `dbo:locationCity`, `dbo:locationCountry` and `dbo:location`.

In addition to using the properties of the DBpedia ontology, some combinations have also been associated with properties of other ontologies. This only happens in very few cases, for example the combination `know as` has been associated with `owl#sameAs`. The other case is that of the verb `to be` which has been associated with the property `rdfs:type` which was introduced in the previous week and will be discussed again later.

### Problems encountered
As discussed in the previous week, the conversion of verbs + prepositions into properties of the dbpedia ontology is a very laborious task since one or more properties from a list of 1200 DBpedia properties must be matched with a combination of verb + preposition. For each combination we search in web pages like [context.reverso.net][3] for phrases containing that combination, so we can learn in which cases they are used. We also look for synonyms of the combination in web pages like [thesaurus.com][4]. The last step is to search among the Object Properties which is the most accurate for the combination.

Mainly we have found a problem with certain prepositions like `in`, `during`, `from`, `to`. These, together with a verb, usually refer to a moment in time, e.g. the sentences `Cameroon played in 1960`, `Burns played for the Tigers from 1914 to 1917`, `He served during his first days in politics`. The problem arises because there are no properties that refer to years or temporal moments as shown in the previous examples. It is recalled that for the moment we are only taking into account the properties that relate two entities (ObjectProperties) since they are the most interesting to deal with. In order to cover verbs with this type of prepositions we would have to include in the process the DatatypeProperties, for example: `dbo:activeYearsStartDate`, `dbo:releaseDate`, `dbo:formationYear`, etc.

Including DataTypes would also introduce more complexity to the application since it would be necessary to determine among all the possible properties which one is the most accurate, this happens for example in the case in which we talk about a specific year since there are many DatatypesProperties that refer to years (formationYear, birthYear, deathYear, etc.). In some cases, looking at the domain of the property may not be enough.
Also, it should be noted that if we are talking about a date or a year, convert this string to an `xsd:gYear` or `xsd:date` literal.

The current status of the verb and preposition lexicalization table can be found [here][5].

## Changes in text to RDF translation
During this week some improvements have been introduced to the triplet processing. The most important one is the strategy to select a property from a list of possible ones. This happens when there are several possible lexicalizations for a certain combination. An example of this is the following:
`"play at": ["https://dbpedia.org/ontology/ground", "https://dbpedia.org/ontology/location", "http://dbpedia.org/ontology/tenant"]`

The first thing that has been done is to download the latest version of the DBpedia ontology from their [download][6] page. In the pipeline the ontology is read using the **rdflib** library and the types of the resources identified by DBpedia Spotlight (Name entity) are extracted. If, for a combination, a list of possible lexicalizations is received from the lookup table, the range and domain of each of the possible lexicalizations are checked. That property that contains the same rank and domain as the classes of the resources identified in the subject and object will be the chosen one.

There are properties that have no rank, domain or both. For all possible lexicalizations a score is calculated by comparing whether the class of the subject and the class of the object are the same (score = 2 matches range and domain, score = 1 matches range or domain, score = 0 matches neither). Always try to choose the property that best matches the identified entities.

### The case of the verb to be
The case of the verb to be is special as it does not follow the same pattern as the other combinations. The verb to be without preposition is lexicalized as `http://www.w3.org/1999/02/22-rdf-syntax-ns#type`. 

As already discussed during [last week][7] the main problem in dealing with this verb is that the object should not be an entity, i.e. we should not use a resource as the third element of the triple. For example in the sentence `Obama is the president` you should get `https://dbpedia.org/page/Barack_Obama`,`http://www.w3.org/1999/02/22-rdf-syntax-ns#type`,`https://dbpedia.org/ontology/president`. Notice that the third element, in its URI contains ontology and not page. The erroneous translation would be the following: `https://dbpedia.org/page/Barack_Obama`,`http://www.w3.org/1999/02/22-rdf-syntax-ns#type`,`https://dbpedia.org/page/President`.

This presents the problem of how to determine which DBpedia ontology class corresponds to the object in the text triplet. We cannot use DBpedia Spotlight since it only serves to identify Name Entities, i.e. resources. As a first approach, a new lexicalization table for nouns has been created and can be consulted [here][8]. The key is the text that should be found in the text triplet object and the value is its lexicalization. At the moment the elements inside the lexicalization table are only those that have been extracted from the URI, i.e. if the uri is `http://dbpedia.org/ontology/PublicTransitSystem` a new entry is created in the dictionary with the key `public transit system` and the URI as value.

This new lexicalization table has been built with the following python [script][9], here is a sample of this file:

```json
{
    "site of special scientific interest": "http://dbpedia.org/ontology/SiteOfSpecialScientificInterest",
    "natural place": "http://dbpedia.org/ontology/NaturalPlace",
    "historical province": "http://dbpedia.org/ontology/HistoricalProvince",
    "soap character": "http://dbpedia.org/ontology/SoapCharacter",
    "table tennis player": "http://dbpedia.org/ontology/TableTennisPlayer",
    "department": "http://dbpedia.org/ontology/Department",
    "american football player": "http://dbpedia.org/ontology/AmericanFootballPlayer",
    "comic strip": "http://dbpedia.org/ontology/ComicStrip",
    "manhua": "http://dbpedia.org/ontology/Manhua",
    "stream": "http://dbpedia.org/ontology/Stream",
    "dam": "http://dbpedia.org/ontology/Dam",
    "mosque": "http://dbpedia.org/ontology/Mosque",
    "educational institution": "http://dbpedia.org/ontology/EducationalInstitution",
    "naruto character": "http://dbpedia.org/ontology/NarutoCharacter",
    "shopping mall": "http://dbpedia.org/ontology/ShoppingMall",
    "record label": "http://dbpedia.org/ontology/RecordLabel",
    "speedway league": "http://dbpedia.org/ontology/SpeedwayLeague",
    "unit of work": "http://dbpedia.org/ontology/UnitOfWork",
    "automobile": "http://dbpedia.org/ontology/Automobile"
}
```
The idea is to add more synonyms of the dbpedia classes, for example add `teacher` as `http://dbpedia.org/ontology/Professor`, and cover more cases. During the next week we will explore in which cases no valid lexicalization is found and add these lexicalizations to the table.

We will discuss with the tutor if this approach is the best option or if there is a better way to deal with these cases.

### Other changes
Previously all resources identified by Spotlight were extracted to build RDF triples. If several entities were obtained for the subject or for the object, a triple was constructed for each combination of both, this produced a lot of erroneous RDF triples, for example many times it constructed a triple with the subject `https://dbpedia.org/page/The`. 
Now, to build the subject of the triples only one element identified by Spotligth is chosen, usually the one that contains more than one word in its surface form.

Fixed a bug that caused that only those resources identified by Spotlight with surface form of one word were used, i.e. if in the text `Alain Connes` was identified as `https://dbpedia.org/page/Alain_Connes` this reference was not used since the text is composed of two words.

Several bugs related to the treatment of verb prepositions have been fixed.

A new function has been introduced to create a graph with the generated RDF triples.

## Firsts results
These are a sample of the results obtained. To see all the results obtained from our sample set (11 dbpedia abstracts at the top of every coding week python script cwX.py) go to [here][10]. For each sentence, the extracted text triples and RDF triples are shown. Only sentences that are simple (a verb or an aux + verb) have been considered.

```
**In Myanmar, the Wa language is the de facto official language of Wa State.**
Khmer | is In | Myanmar
http://dbpedia.org/resource/khmer_language | http://dbpedia.org/ontology/locationCity | http://dbpedia.org/resource/myanmar
--------------------------------------------------
**Ethnologue identifies 168 Austroasiatic languages.**
Ethnologue | identifies | 168 Austroasiatic languages
http://dbpedia.org/resource/ethnologue | identifies | http://dbpedia.org/resource/austroasiatic_languages
Ethnologue | identifies | 168 Austroasiatic languages
http://dbpedia.org/resource/ethnologue | identifies | http://dbpedia.org/resource/languages_of_india
--------------------------------------------------
**He was a community organizer in Chicago before earning his law degree.**
Obama | was before | earning his law degree
http://dbpedia.org/resource/barack_obama | http://www.w3.org/1999/02/22-rdf-syntax-ns#type | http://dbpedia.org/resource/juris_doctor
--------------------------------------------------
**Drexler served as mentor to Adolf Hitler during his early days in politics.**
Anton Drexler | served as | mentor to Adolf Hitler
http://dbpedia.org/resource/anton_drexler | http://dbpedia.org/ontology/occupation | http://dbpedia.org/resource/mentorship
Anton Drexler | served as | mentor to Adolf Hitler
http://dbpedia.org/resource/anton_drexler | http://dbpedia.org/ontology/occupation | http://dbpedia.org/resource/adolf_hitler
Anton Drexler | served during | his early days in politics
http://dbpedia.org/resource/anton_drexler | http://dbpedia.org/ontology/militaryService | http://dbpedia.org/resource/early_childhood_education
Anton Drexler | served during | his early days in politics
http://dbpedia.org/resource/anton_drexler | http://dbpedia.org/ontology/militaryService | http://dbpedia.org/resource/day
Anton Drexler | served during | his early days in politics
http://dbpedia.org/resource/anton_drexler | http://dbpedia.org/ontology/militaryService | http://dbpedia.org/resource/politics
--------------------------------------------------
**He is a Professor at the Collège de France, IHÉS, Ohio State University and Vanderbilt University.**
Alain Connes | is | a Professor at the Collège de France
http://dbpedia.org/resource/alain_connes | http://www.w3.org/1999/02/22-rdf-syntax-ns#type | http://dbpedia.org/ontology/Professor
Alain Connes | is | a Professor at the Collège de IHÉS
http://dbpedia.org/resource/alain_connes | http://www.w3.org/1999/02/22-rdf-syntax-ns#type | http://dbpedia.org/ontology/Professor
```

It can be observed that there are many cases in which the generated triples are not correct or do not make much sense. We will explore in depth the functioning of the tool during week 9 and will try to improve it in the remaining time.

## Conclusions
In conclusion, during this week the foundations of the application have been built and the first final results have been achieved. 

In the next week we will test on a large dataset and extract some metrics such as the number of simple and complex sentences that exist in the selected sample, the number of text triplets generated by each type of sentence, the number of rdf triplets that could be extracted from the text triplets, etc.

The last week will be devoted to the construction of two simple web applications, one to generate RDF from the input text and the other to provide users with a tool to contribute to the construction of the verb lexicalization table.

For more information please check the [repository][1] or the [source file of this coding week 8][2].

[1]: https://github.com/Fcabla/DBpedia-abstracts-to-RDF
[2]: https://github.com/Fcabla/DBpedia-abstracts-to-RDF/blob/main/code/codingweeks/cw8.py
[3]: https://context.reverso.net/traduccion/ingles-espanol/
[4]: https://www.thesaurus.com/browse/synonym
[5]: https://github.com/Fcabla/DBpedia-abstracts-to-RDF/blob/main/datasets/verb_prep_property_lookup.json
[6]: https://databus.dbpedia.org/ontologies/dbpedia.org/ontology--DEV
[7]: https://fcabla.github.io/DBpedia-abstracts-to-RDF/coding-week7
[8]: https://github.com/Fcabla/DBpedia-abstracts-to-RDF/blob/main/datasets/classes_lookup.json
[9]: https://github.com/Fcabla/DBpedia-abstracts-to-RDF/blob/main/code/scripts/build_classes_lookup.py
[10]: https://github.com/Fcabla/DBpedia-abstracts-to-RDF/blob/main/results/generated_rdf_triples_cw8.txt