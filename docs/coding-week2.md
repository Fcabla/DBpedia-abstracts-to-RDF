# Attempting to enhance the triples
In this second week I have tried to rethink the whole project and use different approaches to extract my own clauses. We have simplified the problem to get closer to a good base solution.

## Identified problems
After testing the different implementations of ClausIE i have decided that i will not use this tool to build the clausules. This is because as I could see in the previous blog post, the results generated were not very good.
Also, ClausIE formed clausules of size distinct of 3, which is the ideal solution to our problem. For example, ClausIE can form clausules of subj, verb, indirect object, object.

After discussing it with Mariano, my mentor in this project, it has been decided to discard the more complex sentences and work with the simpler ones. Therefore, for the time being, all sentences containing more than one verb will be discarded. Once good results are achieved with this type of texts, we will study the possibility of introducing more complexity to the system.

## Simplify the problem
As mentioned above, for the moment we will only work with simple sentences containing no more than 1 verb. There are two types of verbs, auxiliary verbs and non-auxiliary verbs. In this first approach we have treated both as verbs, here is the code that selects the sentences to be processed:

```Python
def sentences_1_verb(doc):
    sentences = get_sentences(doc)
    results = []
    for s in sentences:
        c = 0
        for token in s:
            if(token.pos == VERB or token.pos == AUX):
                c = c + 1
        if(c == 1):
            results.append(s)
    return results
```
A set of 12 dbpedia abstracts has been prepared for the initial tests, 9 of them are the first ones in the dataset, the rest have been chosen randomly. These examples can be found [here][2] or in the head of [this source file][3]. The complete dataset can be found [here][1]

## Procesing the simple sentences

For each sentence, we first identified the verb and extracted its children. 
The children of a token are those words that are connected (dependency). With spacy you can extract graphs to identify these connections.
![example_dependency_tree](https://github.com/Fcabla/DBpedia-abstracts-to-RDF/tree/main/docs/example_dependency_tree.png)

With the children, dependency subtrees are extracted which are then inspected and classified into subjects or objects.
To classify them the whole subtree is explored, if an element of the subtree corresponds to a subject or object these are added to their corresponding classes. 

Verbs act as predicates in the ideal triplet < subject,predicate,object > (element,property,element).
Here are some results:
```
the 12th - century translations of medieval Islamic works on science and the rediscovery of Aristotelian philosophy|gave|In Europe
the 12th - century translations of medieval Islamic works on science and the rediscovery of Aristotelian philosophy|gave|birth
the 12th - century translations of medieval Islamic works on science and the rediscovery of Aristotelian philosophy|gave|to a flourishing tradition of Latin alchemy
A , or a|is|the first letter and the first vowel letter of the modern English alphabet and the ISO basic Latin alphabet
" a " , and|are|In the English grammar
" a " , and|are|indefinite articles
its variant " an "|are|In the English grammar
its variant " an "|are|indefinite articles
Various anarchist schools of thought|formed|during this period
the Wa language|is|In Myanmar
the Wa language|is|the de facto official language of Wa State
Ethnologue|identifies|168 Austroasiatic languages
Drexler|served|as mentor
Drexler|served|to Adolf Hitler
Drexler|served|during his early days in politics
```
Apparently the tool has difficulty processing sentences that contain two separate subjects with a coordinating conjunction such as "and". For the sentence: "a", and its variant "an" are... two subjects were expected: "a" and its variant "an".

The case in which the subtree does not contain a subject or object but includes an attribute has been included. For example "indefinite articles" has been treated as an object even though the spacy dependency tree has not considered it as such.

## Exploring transitivity
Following Mariano's advice, you can get a lot of information about the components of a sentence simply by looking at the transitivity of the verb. This has been achieved with this function from [here][4]:

```Python
def check_verb(token):
    """Check verb type given spacy token"""
    if token.pos_ == 'VERB':
        indirect_object = False
        direct_object = False
        for item in token.children:
            if(item.dep_ == "iobj" or item.dep_ == "pobj"):
                indirect_object = True
            if (item.dep_ == "dobj" or item.dep_ == "dative"):
                direct_object = True
        if indirect_object and direct_object:
            return 'DITRANVERB'
        elif direct_object and not indirect_object:
            return 'TRANVERB'
        elif not direct_object and not indirect_object:
            return 'INTRANVERB'
        else:
            return 'VERB'
    else:
        return token.pos_
```
Once identified, sentences will be treated differently in the future according to their transitivity. Another factor to take into account is how to treat auxiliary verbs, since they are not transitive or non-transitive.


## Conclusions

In this second week we got rid of ClausIE in order to form our own clauses. We have focused on simplifying the problem to be able to propose a base system on which to improve little by little to be able to process more complicated sentences.

Another possible future solution, instead of improving the system to be able to process more complicated sentences (with multiple verbs) we can try to pre-process the more complex sentences and simplify them into several. A toy example of this: She eats her pie and then walks to the train station -> she eats her pie, she wals to the train station.
Maybe we could split the conjunctions mantaining the subject, although in this case we would loose some information about the order of both actions.


For more information please check the [repository][5].

[1]: https://databus.dbpedia.org/vehnem/text/long-abstracts/2021.05.01
[2]: https://github.com/Fcabla/DBpedia-abstracts-to-RDF/blob/main/datasets/examples.csv
[3]: https://github.com/Fcabla/DBpedia-abstracts-to-RDF/blob/main/code/cw2.py
[4]: https://stackoverflow.com/questions/49271730/how-to-parse-verbs-using-spacy
[5]: https://github.com/Fcabla/DBpedia-abstracts-to-RDF
