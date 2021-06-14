
# First triples generated with parsing trees

In this first week i have been reviewing the code of the last two participants on this proyect, testing the code and making my own version of it in order to generate the first triples.

## Proposed pipeline

The first idea i had to approach this problem is the following pipeline:
    1. Apply dependency parsing 
    2. Form initial clausules or "triples" splitting every line in three components (subject, predicate, object)
    3. Clean the text from the new clausules
    4. Process those clausules to match the ideal triples (individual, property, literal/individual)
    5. Use dbpedia spotlight to transform the subjects into URIs (example -> http://dbpedia.org/resource/example)
    6. Use dbpedia spotlight to try to transform the objects into URIs, if not possible annote them as literals
    7. Use ontology or dictionary to transform the predicates into RDF properties

## Clausules
As [Ishani][1] did last year, in order to form clausules from the raw text i have used [Clausie][2]. I found two implementations of Clausie for Python. The first one is a [wrapper of the original tool][3] that uses Standford nlp dependency parsing trees, the other tool is an [implemetation of the paper using spacy][4] dependency pasing algorithm. Depending on the abstract used, the performance of each tool varies making one better than the other. Here is a brief example

```
#spacy-clausie
[(Elon Reeve Musk, is, a South African-born Canadian-American business magnate, investor, engineer, inventor), (Elon Reeve Musk, is, engineer), (Elon Reeve Musk, is, a South African-born Canadian-American business magnate), (Elon Reeve Musk, is, inventor), (Elon Reeve Musk, is, investor)]
[(He, is, the founder), (He, is, the founder, founder), (He, is, founder)]
[(which, merged, with PayPal of Confinity)]

----------------------------------------------------------------------------------------------------

#pyclausie
Elon Reeve Musk born June 28 1971,is,a South African-born Canadian-American business magnate investor engineer and inventor
He,is,the founder CEO and CTO co-founder and product architect of Tesla Motors co-founder and chairman of SolarCity co-chairman of OpenAI co-founder of Zip2 and founder of X.com of SpaceX
He,is,the founder CEO and CTO co-founder and product architect of Tesla Motors co-founder and chairman of SolarCity co-chairman of OpenAI co-founder of Zip2 and founder of X.com
co-founder and product architect of Tesla Motors,is,CEO
the founder CEO and CTO of SpaceX co-founder and product architect of Tesla Motors co-founder and chairman of SolarCity co-chairman of OpenAI co-founder of Zip2 and founder of X.com,merged,with PayPal of Confinity
```
To generate the clausules with the selected tool we need to split the text by lines an send those to pyclausie. More examples of the performance [here][5]
Both tools do not produce good results on their own, perhaps later the approach of using Clausie to extract the clauses will be changed to one in which the triples are built with just the dependency parse tree and a custom function.
 
## Processing the triples
Many transformations have to be applied to the triplets to improve their quality. For example, one of the transformations applied is to change the subjects of the previously generated clauses to the most common subject that is not in a blacklist.

```
# Original
Barack Hussein Obama II,is,an American politician
an American politician,is,the 44th and current President of the United States
an American politician,is,the 44th and current President
He,is,the first African American to hold the office and the first president born outside the continental United States
the first president,be born,outside the continental United States
a graduate of Columbia University and Harvard Law School where he was president of the Harvard Law Review,be Born,in Honolulu Hawaii
Obama,is,a graduate Born in Honolulu Hawaii
Obama,is,a graduate of Columbia University and Harvard Law School
Obama,is,a graduate where he was president of the Harvard Law Review
Obama,is,a graduate
he,was,president where
he,was,president of the Harvard Law Review
he,was,president
He,was,a community organizer in Chicago
He,was,a community organizer before earning his law degree
He,was,a community organizer

----------------------------------------------------------------------------------------------------

# Subject replaced
Obama,is,an American politician
Obama,is,the 44th and current President of the United States
Obama,is,the 44th and current President
Obama,is,the first African American to hold the office and the first president born outside the continental United States
Obama,be born,outside the continental United States
Obama,be Born,in Honolulu Hawaii
Obama,is,a graduate Born in Honolulu Hawaii
Obama,is,a graduate of Columbia University and Harvard Law School
Obama,is,a graduate where he was president of the Harvard Law Review
Obama,is,a graduate
Obama,was,president where
Obama,was,president of the Harvard Law Review
Obama,was,president
Obama,was,a community organizer in Chicago
Obama,was,a community organizer before earning his law degree
Obama,was,a community organizer
```
This is a first approach to make the transformations between text and RDF easier. It can present some problems since, although normally in a description of an entity the subject of the sentences will be that entity, the selected subject will not always be the correct one in all cases.

## Text to URIs
For the time being, only the first element of the triplets has been correctly replaced. This has been done by querying the dbpedia spotlight service for the raw text. With the response of the service a dictionary has been generated containing as key the surface text and as value the URI of the resource, here are some examples:
```
http://dbpedia.org/resource/barack_obama,is,an american politician
http://dbpedia.org/resource/barack_obama,is,the 44th and current president
http://dbpedia.org/resource/barack_obama,is,the first african american to hold the office and the first president born outside the continental united states
http://dbpedia.org/resource/barack_obama,be born,outside the continental united states
http://dbpedia.org/resource/barack_obama,be Born,in honolulu hawaii
```
It has also been tested to replace the object (third element of the triples) by the noun chunks and by the URIs of dbpedia spotligh. However, this has not produced very good results and we will continue to work on this.


## Conclusions
In this first week most of the time has been spent reviewing the work done previously on this project and getting to grips with the tools used.

As has been shown, the results generated are not good at all. One of the most notable problems is how to translate the second element of the triples (predicate/verb) by properties of the dbpedia ontology (work -> https://dbpedia.org/ontology/occupation).

For more information please check the [repository][6].

[1]: https://ishani-mondal.github.io/
[2]: http://resources.mpi-inf.mpg.de/d5/clausie/clausie-www13.pdf
[3]: https://github.com/AnthonyMRios/pyclausie
[4]: https://github.com/mmxgn/spacy-clausie
[5]: https://github.com/Fcabla/DBpedia-abstracts-to-RDF/tree/main/results/Examples_pyclausie_vs_spacy-clausie.md
[6]: https://github.com/Fcabla/DBpedia-abstracts-to-RDF
