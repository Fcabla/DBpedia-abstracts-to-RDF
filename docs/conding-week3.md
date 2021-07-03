# Attempting to enhance the triples
In this third week i have continued with the approach introduced in week 2 (exploring subtrees) trying to introduce improvements. At the moment we continue with the simplified problem to get closer to a good base solution.

## Coding week 2 results and indentified problems
Here are some of the coding week 2 results:

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

### Including sentences with aux verbs + regular verbs
The first problem that was identified was that sentences with compound verbs, those formed by an auxiliary verb and a regular verb, were being discarded, since when filtering the sentences, the number of sum(auxiliary verbs, regular verbs) was taken into account, for example:

```
The term albedo was introduced into optics by Johann Heinrich Lambert in his 1760 work Photometria.
Professionals of the agricultural science are called agricultural scientists or agriculturists.
ANOVA was developed by the statistician Ronald Fisher.
He was awarded the Fields Medal in 1982.
```

### Split multiple subjects (cc) in a triple into multiple triples
Another problem is that there are cases in which a subject, or the first element of the triple, is made up of several elements. In the sentence `A, or a, | is | the first letter and the first vowel letter of the modern English alphabet and the ISO basic Latin alphabet.`, `A, or a` is identified as the subject of the triple. Ideally, to further simplify the triples and get a better result when translating it to RDF, the subject of `A, or a` should be cleaned up and split into two triples where the subjects would be `A` and `a`.
```
A | is | the first letter and the first vowel letter of the modern English alphabet and the ISO basic Latin alphabet.
a | is | the first letter and the first vowel letter of the modern English alphabet and the ISO basic Latin alphabet.
```
To perform this task, for each triplet, we search for conjunctions in the subject or first element of the triplet. If these conjunctions are found, the punctuation marks and the coordinating conjunction or cc are eliminated. With the remaining elements, new triples are constructed and the original one is eliminated.

### Split multiple objects (cc) in a triple into multiple triples
The same conclusion can be reach with the third element of the triplet or the object of the clausule. In the sentence `A, or a, | is | the first letter and the first vowel letter of the modern English alphabet and the ISO basic Latin alphabet.`, the last part of the sentence `the modern English alphabet and the ISO basic Latin alphabet.` should be splitted into new triples by the conjunctions `the modern English alphabet` and `the ISO basic Latin alphabet`
```
A | is | the first letter and the first vowel letter of the modern English alphabet.
A | is | the first letter and the first vowel letter of the ISO basic Latin alphabet.
a | is | the first letter and the first vowel letter of the modern English alphabet.
a | is | the first letter and the first vowel letter of the ISO basic Latin alphabet.
```
This task is similar to the previous one, looking for conjunctions in the object or third element of the triplet and for each element identified that are not cc or punctuation marks, new triplets are created keeping the first two elements of the triplet.

### Assigning prepositions to the second element of the triple
Otro problema es que las preposiciones se ponian en el tercer elemento de las tripletas. Pienso que las preposiciones deberian estar junto al verbo o el segundo elemento de la tripleta. Un ejemplo es `The term albedo | was introduced | into optics by Johann Heinrich Lambert in his 1760 work Photometria.` donde las preposiciones `into`, `by` y `in` deberian posicionarse con el verbo.
```
The term albedo was introduced into optics by Johann Heinrich Lambert in his 1760 work Photometria.
The term albedo | was introduced into | optics
The term albedo | was introduced | by Johann Heinrich Lambert
The term albedo | was introduced in | his 1760 work Photometria.
```
This has been achieved by searching for prepositions in the first position of the objects in the triplets, i.e. prepositions are searched for in the first word of the third element of the triplets. If a preposition is found it is appended to the verb and removed from the object.


### Completing auxiliary verbs
The last problem identified from the previous results is that, in those sentences that only contain an auxiliary verb, these verbs by themselves do not provide any information, in the sentence `He | is | a Professor at the Collège de France, IHÉS, Ohio State University and Vanderbilt University.` the verb is does not give any information if the first part of the object `a Professor` is not taken into account. Some examples:
```
He | is a Professor at | the Collège de France, IHÉS, Ohio State University and Vanderbilt University.
A | is the first letter of | the modern English alphabet  
A | is the first vowel letter of| the ISO basic Latin alphabet
the Wa language | is, the, facto, official, language, of | Wa, State

```
This was performed by looking at the childs of the auxiliary verbs, those who where attributes of the auxiliary verb or those who were conjunctions of the attributes of the auxiliary verbs. Once we had identified the main words (attr or conjs) we get the admods and determinants to complete the "chunks". Then, for each chunk we form a new triplet accounting if there is a preposition, so we move it next to the verb.

## Birth and death dates
Since wikipedia usually puts the date of birth or date of death of people in the first sentence, a function has been developed that uses certain regex patterns to extract this information, for example:
```
Elon Reeve Musk (/ˈiːlɒn ˈmʌsk/; born June 28, 1971) is a South African-born ...
'individual born 28 June 1971'

Anton Drexler (13 June 1884 – 24 February 1942) was a German far-right political ...
'individual born 13 June 1884', 'individual death 24 February 1942'

Alain Connes (French: [alɛ̃ kɔn]; born 1 April 1947) is a French mathematician ...
'individual born 1 April 1947'
```

## Results
Here are the triples generated with "en_core_web_sm" model
```
[In Europe, the 12th-century translations of medieval Islamic works on science and the rediscovery of Aristotelian philosophy gave birth to a flourishing tradition of Latin alchemy., The subject has also made an ongoing impact on literature and the arts.]
the 12th century translations of medieval Islamic works on science the of Aristotelian philosophy | gave In | Europe
the 12th century translations of medieval Islamic works on science the of Aristotelian philosophy | gave | birth
the 12th century translations of medieval Islamic works on science the of Aristotelian philosophy | gave to | a flourishing tradition of Latin alchemy
rediscovery | gave In | Europe
The subject | has made | an ongoing impact on literature
------------------------------------------------------------------------------------------------------------------------------------------------------
[A, or a, is the first letter and the first vowel letter of the modern English alphabet and the ISO basic Latin alphabet., In the English grammar, "a", and its variant "an", are indefinite articles.]
a | are In | the English grammar
its variant an | are | the English grammar
A | is the first letter | 
A | is the first vowel letter | 
A | is the ISO basic Latin alphabet | 
a | are indefinite articles | 
its variant an | are indefinite articles | 
a | is the first letter | 
------------------------------------------------------------------------------------------------------------------------------------------------------
[ANOVA was developed by the statistician Ronald Fisher.]
ANOVA | was developed by | the statistician Ronald Fisher
------------------------------------------------------------------------------------------------------------------------------------------------------
[]
------------------------------------------------------------------------------------------------------------------------------------------------------
[]
------------------------------------------------------------------------------------------------------------------------------------------------------
[Various anarchist schools of thought formed during this period., In the last decades of the 20th and into the 21st century, the anarchist movement has been resurgent once more.]
Various anarchist schools of thought | formed during | this period
the anarchist movement | has been In | the last decades of the 20th
------------------------------------------------------------------------------------------------------------------------------------------------------
[Professionals of the agricultural science are called agricultural scientists or agriculturists.]
------------------------------------------------------------------------------------------------------------------------------------------------------
[The term albedo was introduced into optics by Johann Heinrich Lambert in his 1760 work Photometria.]
The term albedo | was introduced into | optics
The term albedo | was introduced by | Johann Heinrich Lambert
The term albedo | was introduced in | his 1760 work Photometria
------------------------------------------------------------------------------------------------------------------------------------------------------
[There are around 117 million speakers of Austroasiatic languages., In Myanmar, the Wa language is the de facto official language of Wa State., Ethnologue identifies 168 Austroasiatic languages.]
the Wa language | is In | Myanmar
Ethnologue | identifies | 168 Austroasiatic languages
the Wa language | is the facto official language of | Wa State
------------------------------------------------------------------------------------------------------------------------------------------------------
[]
------------------------------------------------------------------------------------------------------------------------------------------------------
[]
------------------------------------------------------------------------------------------------------------------------------------------------------
[Drexler served as mentor to Adolf Hitler during his early days in politics.]
Drexler | served as | mentor
Drexler | served to | Adolf Hitler
Drexler | served during | his early days in politics
------------------------------------------------------------------------------------------------------------------------------------------------------
[He is a Professor at the Collège de France, IHÉS, Ohio State University and Vanderbilt University., He was awarded the Fields Medal in 1982.]
He | was awarded | the Fields Medal
He | was awarded in | 1982
He | is a Professor at | the Collège de France
He | is a Professor at | IHÉS
He | is a Professor at | Ohio State University
------------------------------------------------------------------------------------------------------------------------------------------------------
```

## Conclusions

During this third week we have improved the extraction of triplets introduced in the second week using simple sentences with a single verb (regular or auxiliary) or with a compound verb (auxiliary and regular).

Even with the improvements introduced some things to improve can be observed such as sentences with very long subject, for example `the 12th century translations of medieval Islamic works on science the of Aristotelian philosophy`. Next week we will explore more complex sentences and how they behave with the developed system. Perhaps the approach of exploring the subtrees of the children of the root will be changed to one using the noun chunks.

Finally, it has been noticed that depending on the model used ("en_core_web_sm" vs "en_core_web_trf") the results change.


For more information please check the [repository][1] or the [source file of this coding week 3][2].

[1]: https://github.com/Fcabla/DBpedia-abstracts-to-RDF
[2]: https://github.com/Fcabla/DBpedia-abstracts-to-RDF/blob/main/code/cw3.py

