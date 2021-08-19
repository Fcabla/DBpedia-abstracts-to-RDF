# Translating text into RDF
During this sixth week it has been proposed how to perform the first approach for the translation of text format triples into RDF format triples, using dbpedia spotlight for Name Entity Recognition. In addition, new improvements have been introduced to the pipeline in relation to correlations.

## Strategy for translating text into RDF

So far we have focused on processing the DBpedia abstract to split it into very simple sentences, so that we could form triples with the structure `subject | predicate | object`. To give an example, for the description of a book called Animalia, with 343 characters one of the extracted sentences is `Animalia | was published in | 1986`.

As mentioned in one of the first [coding weeks][4] the [DBpedia spotlight][5] service will be used to perform these transformations. DBpedia Spotlight is a tool for automatically annotating mentions of DBpedia resources in text, providing a solution for linking unstructured information sources to the Linked Open Data cloud through DBpedia.

The main idea is to query the API with all the text and create a dictionary where the key is the token or term in lowercase and the value is the URI of the resource. With this dictionary the elements identified by spotlight of the subject and object of the triplet will be replaced by their respective URIs.
Another dictionary is also created, which is not being used yet, where the key is the lowercase word and the value is the type of the resource in the DBpedia ontology. 

The following section shows an example of how this tool works.

Although we can convert most of the triple into URIs, identifying the entities in the text, we still have the problem of changing the predicate to a property of the DBpedia ontology. The ideal triple in RDF format would be `resource | property | resource`, however identifying properties with DBpedia spotlight by looking only at the predicate is impossible.
After consulting this problem with my tutor, he has indicated me that I should create a lookup table with the verbs and prepositions. For example in the sentence `Obama | worked as | civil rights attorney` we would look up the verb worked together with the preposition as in the lookup table and it would return the property `https://dbpedia.org/ontology/occupation`. We should also look at the range and domain of the property, as this indicates what type of resources should be in the subject and predicate.

This involves hand-coding the combination of all verbs and prepositions, which is a big job. At the moment 10000 random long dbpedia abstracts have been selected and a list of the most common verbs has been made, so we will start entering in the lookup table from the most common to the rarest ones. These lists can be found in the results/stats section (in pickle or json format) [here][8].

```
Counter({'be': 19400, 'have': 1490, 'play': 1299, 'include': 1182, 'know': 1175, 'locate': 988, 'serve': 836, 'use': 793, 'win': 790, 'release': 761, 'become': 757, 'make': 750, 'take': 612, 'hold': 600, 'base': 598, 'bear': 572, 'build': 505, 'find': 488, 'write': 485, 'publish': 412, 'call': 391, 'produce': 385, 'name': 377, 'found': 376, 'describe': 374, 'work': 373, 'direct': 372, 'compete': 369, 'form': 368, 'represent': 362, 'begin': 354, 'follow': 340, 'create': 338, 'feature': 327, 'establish': 309, 'die': 306, 'lead': 294, 'run': 293, 'receive': 286, 'elect': 278, 'appear': 276, 'record': 269, 'give': 263, 'see': 254, 'own': 254, 'come': 253, 'operate': 250, 'go': 241, 'move': 237, 'refer': 231, 'provide': 230, 'lie': 229, 'reach': 226, 'list': 221, 'retire': 213, 'start': 213, 'join': 208, 'finish': 208, 'consider': 205, 'develop': 202, 'leave': 196, 'live': 195, 'cover': 190, 'contain': 189, 'perform': 189, 'continue': 182, 'open': 181, '-': 180, 'remain': 178, 'consist': 177, 'sell': 174, 'return': 168, 'star': 160, 'set': 153, 'participate': 153, 'appoint': 149, 'occur': 148, 'lose': 145, 'do': 141, 'situate': 140, 'show': 137, 'replace': 137, 'study': 136, 'design': 135, 'say': 132, 'defeat': 132, 'add': 131, 'award': 128, 'marry': 126, 'allow': 126, 'host': 125, 'sign': 124, 'complete': 124, 'support': 123, 'train': 122, 'end': 117, 'involve': 116, 'offer': 116, 'grow': 112, 'mean': 112, 'announce': 110, 'select': 110, 'pass': 109, 'air': 109, 'attend': 108, 'enter': 107, 'promote': 107, 'introduce': 107, 'close': 107, 'kill': 106, 'compose': 105, 'spend': 104, 'place': 103, 'get': 102, 'relate': 102, 'stand': 101, 'change': 101, 'launch': 100, 'bring': 99, 'meet': 98, 'belong': 98, 'exist': 97, 'carry': 97, 'require': 97,  ...
```

To create these lists, two new scripts have been made. The first one [rdf2csv.py][10] reads the ttl file containing long abstracts (can be downloaded from the DBpedia databus) and creates a csv file with a sample, in this case of size 10000.
The second script [most_common_verbs.py][11] reads the previously created csv file and creates a dictionary where the key is the lemmatized verb and the value is the number of times it appears. In this script you can count verbs in simple sentences, complex sentences or any sentence.
In verbs composed by an auxiliary verb and a regular verb only regular verbs have been counted (was rewarded -> rewarded).

## Name entity recognition (NER): DBpedia Spotlight
This technique consists in the identification of entities in texts. For this project, this technique is of great help since it allows us to identify which parts of the text we should translate from raw text into RDF.

Several tools other than Spotlight have been explored to apply NER, such as Spacy and Standford NLP. The problem with these two tools is that they only identify the text entities but do not inform us of the URI in any ontology of the spotted resources.

DBpedia spotlight has been chosen for this task mainly because we are interested in the identified resources being in the DBpedia ontology and because of the limitations of the other tools.

Spotlight follows four steps: Spotting, candidate mapping, disambiguation and linking / stats. For more information on how this tool works visit their [web page][5]. They also have an [API][6] and a [web page with a demo][7].

To use this tool you can set up a local server or use their online API. The first option would be the most optimal for deployment as it would allow unlimited queries in the shortest possible time. To configure the local server, you only need the server (a java file or a docker) and the model.
On the other hand, you can use its online API to make queries, the main problem is that this api has a limited number of API calls and the response time is significantly longer. However, we are currently using its online API because for each execution of the program we are only querying the API once and it is more convenient to test the project while it is being developed. In the future this will be changed to the local server.

This service consists of an API that receives mainly 3 attributes: the text, a confidence level and a support level. The confidence score is a percentage (0 - 1) with which the results will be filtered, the higher the level the less results will be produced. 
On the other hand, the support level consists of how prominent is this entity in Lucene Model, i.e. number of inlinks in Wikipedia.
The tests performed so far have been with a confidence level of 0.3 and a support level of 0.

As mentioned above, the main idea is to query the API with all the text and create several dictionaries to later replace text by URIs.

Here are some examples of terms identified by DBpedia spotlight in a particular abstract:

```
Barack Hussein Obama II is an American politician who is the 44th and current President of the United States. He is the first African American to hold the office and the first president born outside the continental United States. Born in Honolulu, Hawaii, Obama is a graduate of Columbia University and Harvard Law School, where he was president of the Harvard Law Review. He was a community organizer in Chicago before earning his law degree. He worked as a civil rights attorney and taught constitutional law at the University of Chicago Law School between 1992 and 2004. While serving three terms representing the 13th District in the Illinois Senate from 1997 to 2004, he ran unsuccessfully in the Democratic primary for the United States Hou

barack hussein obama ii -> http://dbpedia.org/resource/barack_obama
american -> http://dbpedia.org/resource/united_states
politician -> http://dbpedia.org/resource/politician
current -> http://dbpedia.org/resource/electric_current
president -> http://dbpedia.org/resource/president_of_the_united_states
united states -> http://dbpedia.org/resource/united_states
he -> http://dbpedia.org/resource/jesus
african american -> http://dbpedia.org/resource/african_americans
hold -> http://dbpedia.org/resource/senate_hold
office -> http://dbpedia.org/resource/public_administration
born -> http://dbpedia.org/resource/max_born
continental united states -> http://dbpedia.org/resource/contiguous_united_states
honolulu, hawaii -> http://dbpedia.org/resource/honolulu
obama -> http://dbpedia.org/resource/barack_obama
graduate -> http://dbpedia.org/resource/bachelor's_degree
columbia university -> http://dbpedia.org/resource/columbia_law_school
harvard law school -> http://dbpedia.org/resource/harvard_law_school
harvard law review -> http://dbpedia.org/resource/harvard_law_review
community organizer -> http://dbpedia.org/resource/community_organizing
chicago -> http://dbpedia.org/resource/chicago
law degree -> http://dbpedia.org/resource/juris_doctor
civil rights -> http://dbpedia.org/resource/civil_and_political_rights
attorney -> http://dbpedia.org/resource/attorneys_in_the_united_states
constitutional law -> http://dbpedia.org/resource/constitutional_law
university -> http://dbpedia.org/resource/cornell_university
law school -> http://dbpedia.org/resource/university_of_chicago_law_school
while -> http://dbpedia.org/resource/while
serving -> http://dbpedia.org/resource/incumbent
terms -> http://dbpedia.org/resource/term_of_office
representing -> http://dbpedia.org/resource/head_of_state
13th district -> http://dbpedia.org/resource/new_york's_13th_congressional_district
illinois senate -> http://dbpedia.org/resource/illinois_senate
democratic primary -> http://dbpedia.org/resource/2008_democratic_party_presidential_primaries
hou -> http://dbpedia.org/resource/the_twelve_kingdoms
```

As you can see there are some errors that can perhaps be corrected by fine tuning the confidence level and processing the triples in such a way that the wrong resources are not used, for example `he -> http://dbpedia.org/resource/jesus`.

At the moment, if the triple does not identify an entity in each part (subject and object), it will not be taken into account when forming the final RDF network. In the case where two or more distinct elements are identified in the same part of the triplet, the most important one will be chosen or the triplet will be split into several, one for each identified element (within the subject or object).

## Coreferences
After presenting the previous week's work to my tutor, he indicated that I could use the Spacy plugin [Coreferee][12] to better calculate the correferences. Coreferences occur when one term in a text refers to another, e.g. for the following text the following coreferences are identified:

```
Although he was very busy with his work, Peter had had enough of it. He and his wife decided they needed a holiday. They travelled to Spain because they loved the country very much.
0: he(1), his(6), Peter(9), He(16), his(18)
1: work(7), it(14)
2: [He(16); wife(19)], they(21), They(26), they(31)
3: Spain(29), country(34)
```

Thanks to this tool, the function `fix_subj_complex_sentences` has been re-coded, which searches the previous sentences for new best subjects for the simplified sentence currently being processed. In addition, a new function called `swap_subjects_correferences` has been created, which is executed at the end of the triple processing (text) looking for those triples that have a coreference in the subject, if a better alternative is found, the subject is changed by the found coreference.

```
Alain Connes | is | a French mathematician
He | is | a theoretical physicist
He | is | a Professor at the Collège de France
He | was awarded | the Fields Medal
He | was awarded in | 1982
****************************************************************
Alain Connes | is | a French mathematician
Alain Connes | is | a theoretical physicist
Alain Connes | is | a Professor at the Collège de France
Alain Connes | was awarded | the Fields Medal
Alain Connes | was awarded in | 1982
****************************************************************
```
This makes it easier for DBpedia spotlight to identify entities in the text.

## Other modifications
The first thing that has been done this week was to remove the function [fix_aux_verbs][3] following the advice of my tutor Mariano. This is due to the strategy to be used to replace the text with RDF.

Initially I thought that the verb to be by itself did not provide any information, so when it was the case, part of the object was added to the predicate, for example in the sentence `Alain Connes | is | a French mathematician ` it was reconstructed as `Alain Connes | is a French | mathematician`.

According to my tutor, when the verb to be appears by itself it should be replaced by the `rdf:type` property, which makes sense.

After trying to remove the function and inspect the results I have some doubts that I will discuss with my tutor, for example in the sentence `Alain Connes | is | a Professor at the Collège de France` I suppose that Alain connes will be of type professor and place of work COllege de France, but a resource can be of type Professor? should I replace the resource professor by the type (DBpedia) of the resource professor (in this case it is professor)?

## Conclusions
In conclusion, this week we have tested different tools and declared a plan for the translation of the texts in the triples into RDF. We have also continued to improve the text processing with the use of the coreference plugin. I still consider that the splitting of the objects in the triples should be improved as in some cases very strange sub triples are produced.

During the next week I will be creating the lookup table and the mechanism to substitute the predicates by the properties inside the lookup table, as well as improving the translation of the objects and subjects. In weeks 9 and 10 the web application will be built, by command line and some statistics and benchmarks will be extracted.

For more information please check the [repository][1] or the [source file of this coding week 6][2].

[1]: https://github.com/Fcabla/DBpedia-abstracts-to-RDF
[2]: https://github.com/Fcabla/DBpedia-abstracts-to-RDF/blob/main/code/codingweeks/cw6.py
[3]: https://github.com/Fcabla/DBpedia-abstracts-to-RDF/blob/b1eef7fb69cbf01bde50ccf5c51571351794eaa6/code/codingweeks/cw5.py#L422
[4]: https://fcabla.github.io/DBpedia-abstracts-to-RDF/coding-week1
[5]: https://www.dbpedia-spotlight.org/
[6]: https://www.dbpedia-spotlight.org/api
[7]: https://www.dbpedia-spotlight.org/demo/
[8]: https://github.com/Fcabla/DBpedia-abstracts-to-RDF/blob/main/results/stats
[9]: https://github.com/Fcabla/DBpedia-abstracts-to-RDF/blob/main/results/stats/complex_sentences_common_verbs.json
[10]: https://github.com/Fcabla/DBpedia-abstracts-to-RDF/blob/main/code/scripts/rdf2csv.py
[11]: https://github.com/Fcabla/DBpedia-abstracts-to-RDF/blob/main/code/scripts/most_common_verbs.py
[12]: https://spacy.io/universe/project/coreferee