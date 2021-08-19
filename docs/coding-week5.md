# Complex sentences 2 and building the application
In the fifth week of development of the GSoC project I have focused on further improving the processing of more complex sentences as well as adapting all the previous code to work with this type of sentences. I have also made some modifications and improvements to some of the functions developed during the previous weeks.

## Data structure
The first important change introduced during this week has been to replace the data structure that was being used so far, which was a list of lists ([[],[],[],[]]) by a class defined by me called Triplet.
This class has three attributes, which correspond to the three lists of tokens (subjet, predicate and object), and a couple of methods to print correctly the triples.

```python
class Triple:
    def __init__(self, subj, pred, obj):
        self.subj = subj
        self.pred = pred
        self.objct = obj
    
    def get_all_tokens(self):
        return self.subj + self.pred + self.objct

    def __repr__(self):
        # subj | pred | obcjt
        return f"{' '.join([x.text for x in self.subj])} | {' '.join([x.text for x in self.pred])} | {' '.join([x.text for x in self.objct])}"

    def __str__(self):
        # subj pred obcjt
        return f"{' '.join([x.text for x in self.subj])} {' '.join([x.text for x in self.pred])} {' '.join([x.text for x in self.objct])}"

```

In the coming weeks, when we will explore how to convert text triples into triples with URIs, we will probably define a new class or adapt the Triplet class to store both the text version and the version with URIs.


## Better sentence simplifier
During [coding week 4][3] several techniques or procedures were discussed to simplify the most complex sentences, with several verbs, and it was concluded that the best procedure to simplify the sentences was to look at those tokens that represented clause modifiers (acl, relcl, advcl, etc.).

The main idea was to calculate the subtrees of each clause modifier and thus extract the simplest sentences. The problem of this approach is to know when and how to cut the subtree since in many occasions the new generated sentences were missing tokens or had tokens from another subphrase.
An example of the previous algorithm with advcl (adverbial clause modifier) tokens:

```python
sents = []
for token in adv_clau:
        sent = []
        for token_children in token.subtree:
            sent.append(token_children.text)
            rights = [t for t in token_children.rights]
            if any([t.dep_ == "advcl" for t in rights]):
                break
        sents.append(sent)
return sents
```

As it can be observed, first the subtree of the tokens that are clause modifiers was explored and for each token of the subtree those tokens in the right part of the sentence that are of the advcl type are explored, if it is the case the exploration of the subtree is cut and the new simple sentence is generated.
The problem occurs when the sentences contain relations with advcl tokens at the beginning of the simple sentences, generating very short and meaningless sentences. Another problem is that when processing the sentences by type of clause modifier, the order of the triples is lost, which makes it more complicated in the future to determine which is the ideal subject of these simple sentences, since normally the subject of these simple sentences are usually pronouns such as who, that, he, its, etc. This will be explained later.

To solve these problems, the algorithm has been changed. The first step is to identify and store tokens of the type acl, advcl, relcl and conjunctions whose direct ancestor is a verb, without making distinctions, all these tokens are stored in the same list. Then the simple sentence containing the token of type root is constructed, in the same way as in the previous week.

For each clause in the list of clause modifiers, the subtree is calculated and the subtree is scanned for tokens containing other clause modifiers, i.e. the simple sentence being processed contains more verbs than it should have.

If it contains any token of this type what is done now is to eliminate from the sentence to be generated the subtree of the clause that should not be in the sentence, the algorithm is as follows:

```python
sentences = []
    for token in clauses:
        subtree = [t for t in token.subtree]
        substract_tokens = []
        for t in subtree:
            if t.dep_ in ["advcl", "acl", "relcl"] and t != token:
                substract_tokens.append(t)
        for st in substract_tokens:
            substract_subtree = [t for t in st.subtree]
            subtree = [x for x in subtree if x not in substract_subtree]
        # Make span
        sentences.append(subtree[0].doc[subtree[0].i : subtree[-1].i+1])
    return sentences
```

In order to use the same function for all types of sentences, instead of storing the generated simple sentences as lists of tokens, an object of type Span of Spacy is constructed, for example at the time of constructing the simple sentence with the token root:

```python
# store in sent all the tokens until one have an ancestor that corresponds to a clausule modifier (advcl, relcl, acl)
start = sent[0].i
end = sent[-1].i+1
result_sentences.append(doc[start : end])
```
In this case a Span object is being formed from the index of the first token to the index of the last token in the sent list. The Span type objects at the end are slices of the original document, for example this type of objects are generated when we use doc.sents, which returns a list of the sentences (Spans) of the document.

## Fixing subjects in simple sentences (from complex sentences)
As discussed last week, one of the main problems with simplifying a complex sentence into several sub-sentences is the loss of subject information in these sub-sentences. A clear example of this is the following: The complex sentence `Alchemy is an ancient branch of natural philosophy, a philosophical and protoscientific tradition that was historically practiced in China, India, the Muslim world, and Europe.` is divided into the following two subphrases `Alchemy | is | an ancient branch of natural philosophy , a philosophical and protoscientific tradition` and `that | was practiced | in China , India , the Muslim world , and Europe`. In this last simple sentence we can observe that the subject of the triplet is `that`, which does not offer any real information about the subject. Ideally the subject for that sentence would be the term `Alchemy`, which coincides with the subject of the previous sentence.

Therefore, the following solution has been proposed to detect in which sentences this problem appears and how to solve it. First, we look for those triplets that contain a clause modifier in the predicate, since these are the ones that come from complex sentences. Once located, we look for the subject of the current triple and the subject of the previous sentence in order to compare their dependency tags.

From the examples available, the following conclusion has been reached:
1. if the verb token is of type acl, the new subject is the subject of the previous sentence.
2. If the verb token is of type conj and its direct ancestor is a verb, the new subject is the subject of the previous sentence.
3. If the verb token is any other type of clause:
4.  If the current subject is passive and the previous subject is nominal, the new subject is the subject of the previous sentence.
5.  If the current subject and the previous subject are different, the new subject is the subject of the previous sentence.
6.  If the present subject and the preceding subject are both nominal, the new subject is the subject of the preceding sentence. 
7. If none of the above is true, do not modify the triplet.

Some examples:
```
that | was practiced | in China , India , the Muslim world , and Europe
Alchemy | was practiced | in China , India , the Muslim world , and Europe

some of which | are | in use
a basic set of laboratory techniques , theories , and terms | are | in use

that | is | sceptical of authority
Anarchism | is | sceptical of authority

which | can be separated | into revolutionary and evolutionary tactics
Anarchism | can be separated | into revolutionary and evolutionary tactics

who | is | the 44th and current President of the United States
Barack Hussein Obama II | is | the 44th and current President of the United States

humans | lived | long before the establishment of formal states , realms or empires
back to prehistory | lived | long before the establishment of formal states , realms or empires
```
As can be shown in the last example, it does not always produce better results, in some cases the subject of the simplified sentence provides more information than the new subject. As more examples are tested, conditions or cases will be included to improve the selection of new subjects.

The following [web page][4] has been very helpful in understanding how the clause modifiers behave and deciding which part of the old triplet corresponded to the subject of the new triplet.

## Fixing triplets with xcomp in the predicate and verbs conjunctions
While testing the new enhancements it was discovered that there was a type of sentence that did not fit into the pipeline designed so far. This type of sentences are those that contain multiple verbs and are conjunctions that arise from the root verb. For example the sentence: `Alchemists attempted to purify, mature, and perfect certain materials`. 

If the sentence is processed with last week's algorithm it produces the following subphrases: `Alchemists attempted to purify, mature, and perfect certain materials.` and `mature`. It does not split the sentence correctly and generates a sentence that does not make any sense since it has only one token.

To achieve this, the first thing to do is to identify the conjunctions that exist within the triple object. In turn these are eliminated from the object of the triplet, because the aim is to obtain the part of the object that has nothing to do with the conjunctions, in this case it would be `certain materials`.

Since normally the conjunctions are separated by coordinating conjunction (for example and) or with punctuation tokens, these are eliminated from the new object.

Once the new object, the original predicate and the conjunctions are obtained, a new triple is generated for each conjunction, so that in each iteration the current conjunction is replaced by the verb in the predicate. The result of the above sentence is the following: `Alchemists | attempted to purify | certain materials`, `Alchemists | attempted to mature | certain materials` and `Alchemists | attempted to perfect | certain materials`.

Currently only sentences starting the conjunctions list with a token of type xcomp are supported, it is not known whether such sentences can be given from a verb other than xcomp.

## Better conjunction splitter in subjects and objects
During the development of this week we could observe that there were cases in which the functions to divide the subject and the object in several from conjunctions did not work well.

### Subjects
In previous weeks, the division of a subject into several subjects was done by simply looking for conjunctions, if any were found they were eliminated from the original subject and a new triplet was constructed. In turn, if cc or punct tokens were found, they were eliminated. The main problem with this approach is that some information was lost because subject modifiers were not included in the new triples. For example in the subject `Islamic and European alchemists` the following subjects were produced: `Islamic` and `European alchemist`. In the first generated subject it was expected to add the term alchemist.

To solve this, what has been done is to first build the first subject by looking at the ancestor of the first conjunction, in this case the first conjunction is the term `European`, its direct ancestor is a modifier (amod, advmod, nmod, etc.) so we have to keep scaling until the main subject is found, this being the term `alchemist`. From here the first subject is formed, this being `Islamic alchemists`.

Then the same process is followed for each conjunction, if the ancestor of the conjunction of the current iteration is a modifier, a new subject is created with the modifier + the subject. In the case where it is the subject itself, a new subject is created with the direct ancestor of the conjunction and all its child modifiers in the dependency tree.

This process is a bit complicated, for more information see the functions split_conjunctions_subj and split_conjunctions_obj in [source file][2].

### Objects 
Something similar to what happens with subjects can be found for objects. In the original function the tokens were stored from left to right until a token of type cc or punct was found. In that case a new triplet is created with the stored tokens and the search is resumed storing again the tokens to build a new object. The problem is that, except for the first generated object, the triples lost information. 

The new version of the function behaves similarly to the function that splits the subjects. First the main part of the original object is searched and the first sub-object is constructed. For example in the sentence `European alchemists | developed | a basic set of laboratory techniques, theories, and terms` the main part of the object is `a basic set of` since it will be present in all new objects. When joining the main part with the ancestor of the first conjunction we also look for modifiers of that token (in this case laboratory is compound of techniques).

After generating the first sub object `a basic set of laboratory techniques` the same procedure is followed for the identified conjunctions.

This process is a bit complicated, for more information see the functions split_conjunctions_subj and split_conjunctions_obj in [source file][2].

## Results
Here are some of the results obtained with all the functions implemented so far.
```
Barack Hussein Obama II | is an American politician | 
****************************************************************
Barack Hussein Obama II | is | the 44th
****************************************************************
Barack Hussein Obama II | is | the current President
****************************************************************
The term albedo | was introduced into | optics
****************************************************************
The term albedo | was introduced by | Johann Heinrich Lambert
****************************************************************
The term albedo | was introduced in | his 1760 work Photometria
****************************************************************
Agricultural science | is a broad multidisciplinary field of | biology
****************************************************************
Agricultural science | encompasses | the parts of natural sciences
****************************************************************
Agricultural science | encompasses | the parts of economic
****************************************************************
Alchemy | was practiced in | China
****************************************************************
Alchemy | was practiced in | India
****************************************************************
```
All the results can be found [here][5]

## Conclusions
We can conclude that this week we have improved a lot the part of the project that is in charge of processing the document to generate simpler sentences with which in the future we will produce triples formed by URIs.

It is true that even so, some errors have been identified, or very specific cases that generate low quality triples. There are a large number of phrase configurations, so it is very complicated to create a program that is able to simplify and generate good triples for all cases.
As the development progresses, new cases will be introduced to be considered within the functions developed so far or even new functions that deal with some type of triplet, as has happened with the function fix_xcomp_conj.

From now on I will focus on the translation of generated triples, formed by text, into triples formed by URIs, in RDF. Next week I will explore different techniques and tools to achieve this translation.

For more information please check the [repository][1] or the [source file of this coding week 5][2].

[1]: https://github.com/Fcabla/DBpedia-abstracts-to-RDF
[2]: https://github.com/Fcabla/DBpedia-abstracts-to-RDF/blob/main/code/codingweeks/cw5.py
[3]: https://fcabla.github.io/DBpedia-abstracts-to-RDF/coding-week4
[4]: https://universaldependencies.org/
[5]: https://github.com/Fcabla/DBpedia-abstracts-to-RDF/tree/main/results/processed_sentences_cw5.md



