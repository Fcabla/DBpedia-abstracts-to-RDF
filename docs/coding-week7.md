# Building the lexicalization lookup table
This week we have focused on the construction of the lookup table that will allow us to apply lexicalization to infer the property (predicate) of the ontology from the verb + preposition of a sentence. As we did when developing the pipeline to process the sentences, we will only use sentences with simple verbs.

## Length and content of the lexicalization table
Once we have understood the process to transform the predicates into properties of the DBpedia ontology, we need to consider which verbs and prepositions we are going to take into account. Obviously we cannot take into account all the combinations since it would take too much time to develop the table.

To get an idea of which verbs and which prepositions to consider, we have taken a sample of 10,000 DBpedia abstracts and extracted the verbs and prepositions that appear in simple sentences (with only one verb). The results can be seen in the following [directory][3]. For each type of sentence, the most frequent verbs, prepositions and verbs + prepositions have been calculated.

For example, these are the ten [most common verbs in simple sentences][4]:
```
"be": 7655,
"have": 482,
"play": 313,
"locate": 281,
"serve": 256,
"include": 248,
"win": 243,
"release": 238,
"hold": 212,
"find": 211,
```
Once these lists were constructed, the cumulative sum of the number of occurrences was calculated, in this way we can see how many cases we covered with each sublist of verbs. In the following image you can see the graph where the x-axis is the verbs and the y-axis is the percentage of cases covered from the X to the origin (cumulative sum).
![cumsum_verbs](https://raw.githubusercontent.com/Fcabla/DBpedia-abstracts-to-RDF/main/results/cumsum_verbs.png)

![cumsum_prepositions](https://raw.githubusercontent.com/Fcabla/DBpedia-abstracts-to-RDF/main/results/cumsum_prepositions.png)


These plots have been obtained from the following [python script][5]

## List of properties

```python
from rdflib import Graph, OWL
props = []
for s, p, o in g.triples((None, None, OWL.ObjectProperty)):
    props.append(s)
```


## Conclusions (TODO)
In conclusion, ...

During the next week ....

For more information please check the [repository][1] or the [source file of this coding week 6][2].

[1]: https://github.com/Fcabla/DBpedia-abstracts-to-RDF
[2]: https://github.com/Fcabla/DBpedia-abstracts-to-RDF/blob/main/code/cw7.py
[3]: https://github.com/Fcabla/DBpedia-abstracts-to-RDF/blob/main/results/stats
[4]: https://github.com/Fcabla/DBpedia-abstracts-to-RDF/blob/main/results/stats/simple_sentences_common_verbs.json
[5]: https://github.com/Fcabla/DBpedia-abstracts-to-RDF/blob/main/code/cumsum_common_verbs_preps.py
