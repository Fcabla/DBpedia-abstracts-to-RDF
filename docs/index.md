# Gsoc 2021 Blog
A small blog to track my progress on the DBpedia Gsoc 2021 project.

## 17/05/2021 Results announced
I have been chosen to develop a tool to convert DBpedia abstracts into RDF triples, I can't wait to get started!
Here you can find more information about the [project](https://summerofcode.withgoogle.com/projects/#6560166180290560)

## 3/06/2021 Community Bonding: First community meeting
Call to meet with almost all DBpedia/GSoC mentors and students and get to know all the projects.
Here you can find a linkedin publication about this [meeting](https://www.linkedin.com/posts/dbpedia_students-mentors-gsoc-activity-6806219042404282369-rpOy)

## Coding week 1 (07/06/2021 - 14/06/2021)
In this first week i have been reviewing the code of the last two participants on this proyect, testing the code and making my own version of it in order to generate the first triples. Explained in detail [here](https://fcabla.github.io/DBpedia-abstracts-to-RDF/coding-week1)

## Coding week 2 (14/06/2021 - 21/06/2021)
In this second week I have tried to rethink the whole project and use different approaches to extract my own clauses. We have simplified the problem to get closer to a good base solution. Explained in detail [here](https://fcabla.github.io/DBpedia-abstracts-to-RDF/coding-week2)

## Coding week 3 (21/06/2021 - 28/06/2021)
In this third week i have continued with the approach introduced in week 2 (exploring subtrees) trying to introduce improvements. At the moment we continue with the simplified problem to get closer to a good base solution. Explained in detail [here](https://fcabla.github.io/DBpedia-abstracts-to-RDF/coding-week3)

## Coding week 4 (28/06/2021 - 05/07/2021)
During this fourth week we have been studying the type of tokens that make up complex sentences containing more than one verb and how to simplify the sentences entered into the system. Explained in detail [here](https://fcabla.github.io/DBpedia-abstracts-to-RDF/coding-week4)

## Coding week 5 (05/07/2021 - 12/07/2021)
In the fifth week of development of the GSoC project I have focused on further improving the processing of more complex sentences as well as adapting all the previous code to work with this type of sentences. I have also made some modifications and improvements to some of the functions developed during the previous weeks. Explained in detail [here](https://fcabla.github.io/DBpedia-abstracts-to-RDF/coding-week5)

## First evaluation period (12/07/2021 - 16/07/2021)
First evaluation period - students submit evaluations of mentors

## Coding week 6 (12/07/2021 - 19/07/2021)
During this sixth week it has been proposed how to perform the first approach for the translation of text format triples into RDF format triples, using dbpedia spotlight for Name Entity Recognition. In addition, new improvements have been introduced to the pipeline in relation to correlations. Explained in detail [here](https://fcabla.github.io/DBpedia-abstracts-to-RDF/coding-week6)

## Coding week 7 (19/07/2021 - 26/07/2021)
This week we have focused on the construction of the lookup table that will allow us to apply lexicalization to infer the property (predicate) of the ontology from the verb + preposition of a sentence. As we did when developing the pipeline to process the sentences, we will only use simple sentences with verbs. Explained in detail [here](https://fcabla.github.io/DBpedia-abstracts-to-RDF/coding-week7)

## Coding week 8 (26/07/2021 - 02/08/2021)
In this eighth week we have dedicated ourselves to build the necessary functions to correctly convert text triples into RDF triples. In addition, we have filled in the lexicalization table a bit more and fixed some bugs. Explained in detail [here](https://fcabla.github.io/DBpedia-abstracts-to-RDF/coding-week8)

## Coding week 9 (02/08/2021 - 09/08/2021)
During the ninth week we have been testing the performance of the application by testing it with 10000 DBpedia abstracts. With this we intend to obtain several metrics such as the number of simple sentences, complex sentences, number of lexicalization failures, etc. In addition, the local DBpedia spotlight server has been installed to use it instead of the online API. Explained in detail [here](https://fcabla.github.io/DBpedia-abstracts-to-RDF/coding-week9)

## Coding week 10 (09/08/2021 - 16/08/2021)
WIP. Explained in detail [here](https://fcabla.github.io/DBpedia-abstracts-to-RDF/coding-week10)

## Final evaluation period (16/08/2021 - 23/08/2021)
Students submit their code, write tests and documentation, and submit a final evaluation of their Mentor
