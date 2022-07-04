"""
Coding week 9
Author: Fernando Casabán Blasco
"""

import coreferee
import spacy
import re
from spacy.symbols import nsubj, VERB, AUX, PUNCT
from spacy import displacy
import pandas as pd
import requests
import json
import copy
from rdflib import Graph, OWL, RDFS, RDF, URIRef, Literal
import time

############
# Examples #
############

banned_subjects = ["he", "she", "it", "his", "hers"]
SPOTLIGHT_LOCAL_URL = "http://localhost:2222/rest/annotate/"
SPOTLIGHT_ONLINE_API = "https://api.dbpedia-spotlight.org/en/annotate"
MODIFIERS = ["compound", "amod", "nummod", "nmod", "advmod", "npadvmod"]
#USE_COMPLEX_SENTENCES = False
USE_COMPLEX_SENTENCES = True
PROP_LEXICALIZATION_TABLE = "../../datasets/verb_prep_property_lookup.json"
CLA_LEXICALIZATION_TABLE = "../../datasets/classes_lookup.json"
DBPEDIA_ONTOLOGY = "../../datasets/dbo_ontology_2021.08.06.owl"
UNKOWN_VALUE = "UNK"
DEFAULT_VERB = "DEF"
DATASET_PATH = "../../datasets/long-abstracts-sample.csv"

# test_examples = [
#     "Alchemy (from Arabic: al-kīmiyā; from Ancient Greek: khumeía) is an ancient branch of natural philosophy, a philosophical and protoscientific tradition that was historically practiced in China, India, the Muslim world, and Europe. In its Western form, it is first attested in a number of pseudepigraphical texts written in Greco-Roman Egypt during the first few centuries CE. Alchemists attempted to purify, mature, and perfect certain materials. Common aims were chrysopoeia, the transmutation of \"base metals\" (e.g., lead) into \"noble metals\" (particularly gold); the creation of an elixir of immortality; and the creation of panaceas able to cure any disease. The perfection of the human body and soul was thought to result from the alchemical magnum opus (\"Great Work\"). The concept of creating the philosophers' stone was variously connected with all of these projects.Islamic and European alchemists developed a basic set of laboratory techniques, theories, and terms, some of which are still in use today. However, they did not abandon the ancients' belief that everything is composed of four elements, and they tended to guard their work in secrecy, often making use of cyphers and cryptic symbolism. In Europe, the 12th-century translations of medieval Islamic works on science and the rediscovery of Aristotelian philosophy gave birth to a flourishing tradition of Latin alchemy. This late medieval tradition of alchemy would go on to play a significant role in the development of early modern science (particularly chemistry and medicine). Modern discussions of alchemy are generally split into an examination of its exoteric practical applications and its esoteric spiritual aspects, despite criticisms by scholars such as Eric J. Holmyard and Marie-Louise von Franz that they should be understood as complementary. The former is pursued by historians of the physical sciences, who examine the subject in terms of early chemistry, medicine, and charlatanism, and the philosophical and religious contexts in which these events occurred. The latter interests historians of esotericism, psychologists, and some philosophers and spiritualists. The subject has also made an ongoing impact on literature and the arts.",
#     "A, or a, is the first letter and the first vowel letter of the modern English alphabet and the ISO basic Latin alphabet. Its name in English is a (pronounced ), plural aes. It is similar in shape to the Ancient Greek letter alpha, from which it derives. The uppercase version consists of the two slanting sides of a triangle, crossed in the middle by a horizontal bar. The lowercase version can be written in two forms: the double-storey a and single-storey ɑ. The latter is commonly used in handwriting and fonts based on it, especially fonts intended to be read by children, and is also found in italic type.In the English grammar, \"a\", and its variant \"an\", are indefinite articles.",
#     "Analysis of variance (ANOVA) is a collection of statistical models and their associated estimation procedures (such as the \"variation\" among and between groups) used to analyze the differences among means. ANOVA was developed by the statistician Ronald Fisher. ANOVA is based on the law of total variance, where the observed variance in a particular variable is partitioned into components attributable to different sources of variation. In its simplest form, ANOVA provides a statistical test of whether two or more population means are equal, and therefore generalizes the t-test beyond two means.",
#     "Allan Dwan (born Joseph Aloysius Dwan; 3 April 1885 – 28 December 1981) was a pioneering Canadian-born American motion picture director, producer, and screenwriter.",
#     "Animalia is an illustrated children's book by Graeme Base. It was originally published in 1986, followed by a tenth anniversary edition in 1996, and a 25th anniversary edition in 2012. Over four million copies have been sold worldwide. A special numbered and signed anniversary edition was also published in 1996, with an embossed gold jacket.",
#     "Anarchism is a political philosophy and movement that is sceptical of authority and rejects all involuntary, coercive forms of hierarchy. Anarchism calls for the abolition of the state, which it holds to be undesirable, unnecessary, and harmful. As a historically far-left movement, it is usually described alongside libertarian Marxism as the libertarian wing (libertarian socialism) of the socialist movement and has a strong historical association with anti-capitalism and socialism. The history of anarchy goes back to prehistory, when humans arguably lived in anarchic societies long before the establishment of formal states, realms or empires. With the rise of organised hierarchical bodies, scepticism toward authority also rose, but it was not until the 19th century that a self-conscious political movement emerged. During the latter half of the 19th and the first decades of the 20th century, the anarchist movement flourished in most parts of the world and had a significant role in workers' struggles for emancipation. Various anarchist schools of thought formed during this period. Anarchists have taken part in several revolutions, most notably in the Spanish Civil War, whose end marked the end of the classical era of anarchism. In the last decades of the 20th and into the 21st century, the anarchist movement has been resurgent once more.Anarchism employs a diversity of tactics in order to meet its ideal ends which can be broadly separated into revolutionary and evolutionary tactics. There is significant overlap between the two which are merely descriptive. Revolutionary tactics aim to bring down authority and state, having taken a violent turn in the past. Evolutionary tactics aim to prefigure what an anarchist society would be like. Anarchist thought, criticism and praxis have played a part in diverse areas of human society. Criticisms of anarchism include claims that it is internally inconsistent, violent, or utopian.",
#     "Agricultural science is a broad multidisciplinary field of biology that encompasses the parts of exact, natural, economic and social sciences that are used in the practice and understanding of agriculture. Professionals of the agricultural science are called agricultural scientists or agriculturists.",
#     "Albedo (pronounced ; Latin: albedo, meaning 'whiteness') is the measure of the diffuse reflection of solar radiation out of the total solar radiation and measured on a scale from 0, corresponding to a black body that absorbs all incident radiation, to 1, corresponding to a body that reflects all incident radiation.Surface albedo is defined as the ratio of radiosity Je to the irradiance Ee (flux per unit area) received by a surface. The proportion reflected is not only determined by properties of the surface itself, but also by the spectral and angular distribution of solar radiation reaching the Earth's surface. These factors vary with atmospheric composition, geographic location and time (see position of the Sun). While bi-hemispherical reflectance is calculated for a single angle of incidence (i.e., for a given position of the Sun), albedo is the directional integration of reflectance over all solar angles in a given period. The temporal resolution may range from seconds (as obtained from flux measurements) to daily, monthly, or annual averages.Unless given for a specific wavelength (spectral albedo), albedo refers to the entire spectrum of solar radiation. Due to measurement constraints, it is often given for the spectrum in which most solar energy reaches the surface (between 0.3 and 3 μm). This spectrum includes visible light (0.4–0.7 μm), which explains why surfaces with a low albedo appear dark (e.g., trees absorb most radiation), whereas surfaces with a high albedo appear bright (e.g., snow reflects most radiation) .Albedo is an important concept in climatology, astronomy, and environmental management (e.g., as part of the Leadership in Energy and Environmental Design (LEED) program for sustainable rating of buildings). The average albedo of the Earth from the upper atmosphere, its planetary albedo, is 30–35% because of cloud cover, but widely varies locally across the surface because of different geological and environmental features.The term albedo was introduced into optics by Johann Heinrich Lambert in his 1760 work Photometria.",
#     "The Austroasiatic languages , also known as Mon–Khmer , are a large language family of Mainland Southeast Asia, also scattered throughout parts of India, Bangladesh, Nepal, and southern China. There are around 117 million speakers of Austroasiatic languages. Of these languages, only Vietnamese, Khmer and Mon have a long-established recorded history and only Vietnamese and Khmer have official status as modern national languages (in Vietnam and Cambodia, respectively). The Mon language is a recognized indigenous language in Myanmar and Thailand. In Myanmar, the Wa language is the de facto official language of Wa State. Santali is one of the 22 scheduled languages of India. The rest of the languages are spoken by minority groups and have no official status. Ethnologue identifies 168 Austroasiatic languages. These form thirteen established families (plus perhaps Shompen, which is poorly attested, as a fourteenth), which have traditionally been grouped into two, as Mon–Khmer and Munda. However, one recent classification posits three groups (Munda, Nuclear Mon-Khmer and Khasi–Khmuic), while another has abandoned Mon–Khmer as a taxon altogether, making it synonymous with the larger family.Austroasiatic languages have a disjunct distribution across Southeast Asia and parts of India, Bangladesh, Nepal and East Asia, separated by regions where other languages are spoken. They appear to be the extant autochthonous languages of Mainland Southeast Asia (excluding the Andaman Islands), with the neighboring Kra–Dai, Hmong-Mien, Austronesian, and Sino-Tibetan languages being the result of later migrations.",
#     "Barack Hussein Obama II is an American politician who is the 44th and current President of the United States. He is the first African American to hold the office and the first president born outside the continental United States. Born in Honolulu, Hawaii, Obama is a graduate of Columbia University and Harvard Law School, where he was president of the Harvard Law Review. He was a community organizer in Chicago before earning his law degree. He worked as a civil rights attorney and taught constitutional law at the University of Chicago Law School between 1992 and 2004. While serving three terms representing the 13th District in the Illinois Senate from 1997 to 2004, he ran unsuccessfully in the Democratic primary for the United States Hou",
#     "Elon Reeve Musk (/ˈiːlɒn ˈmʌsk/; born June 28, 1971) is a South African-born Canadian-American business magnate, investor, engineer and inventor. He is the founder, CEO, and CTO of SpaceX; co-founder, CEO, and product architect of Tesla Motors; co-founder and chairman of SolarCity; co-chairman of OpenAI; co-founder of Zip2; and founder of X.com which merged with PayPal of Confinity. As of June 2016, he has an estimated net worth of US$12.7 billion, making him the 83rd wealthiest person in the world. Musk has stated that the goals of SolarCity, Tesla Motors, and SpaceX revolve around his vision to change the world and humanity. His goals include reducing global warming through sustainable energy production and consumption, and reducing the \"risk of human extinction\" by \"making life multiplanetary\" by setting up a human colony on Mars. In addition to his primary business pursuits, he has also envisioned a high-speed transportation system known as the Hyperloop, and has proposed a VTOL supersonic jet aircraft with electric fan propulsion, known as the Musk electric jet.",
#     "Anton Drexler (13 June 1884 – 24 February 1942) was a German far-right political leader of the 1920s who was instrumental in the formation of the pan-German and anti-Semitic German Workers' Party (Deutsche Arbeiterpartei – DAP), the antecedent of the Nazi Party (Nationalsozialistische Deutsche Arbeiterpartei – NSDAP). Drexler served as mentor to Adolf Hitler during his early days in politics.",
#     "Alain Connes (French: [alɛ̃ kɔn]; born 1 April 1947) is a French mathematician, and a theoretical physicist, known for his contributions to the study of operator algebras and noncommutative geometry. He is a Professor at the Collège de France, IHÉS, Ohio State University and Vanderbilt University. He was awarded the Fields Medal in 1982."
# ]

test_examples = [
    "Jerome C. \"\"Jerry\"\" Meyer (July 2, 1927 – July 15, 2005) was a Canadian National Champion trainer and Hall of Fame inductee in Thoroughbred racing.Meyer began his career in racing as a jockey but weight gain soon ended that, and at age 18 he turned to the training end of the business. In 1949 he took out his license and went on to a career that spanned seven decades, both in Canada and the United States.Based at Woodbine Racetrack in Toronto, Meyer won most every important stakes the track offered at least once, including three of the Canadian Triple Crown races.Among his early successes in the United States, Meyer won the 1969 inaugural running of the Governor Nicholls Stakes for owner Elmendorf Farm in front of a Labor Day record crowd.Jerry Meyer died of cancer on July 15, 2005, at Princess Margaret Cancer Centre in Toronto."
]

################################
# Classes and helper functions #
################################

class Triple:
    def __init__(self, subj, pred, objct, sent):
        """list of tokens"""
        self.subj = subj
        self.pred = pred
        self.objct = objct
        self.sent = sent

    def get_copy(self):
        return Triple(self.subj.copy(), self.pred.copy(), self.objct.copy(), self.sent)

    def get_all_tokens(self):
        """
        Returs a list with all the tokens in the triple
        """
        return self.subj + self.pred + self.objct

    def set_rdf_triples(self, subj, pred, objct):
        self.subj_rdf = subj
        self.pred_rdf = pred
        self.objct_rdf = objct

    def get_rdf_triple(self):
        return f"{self.subj_rdf} | {self.pred_rdf} | {self.objct_rdf}"

    def __repr__(self):
        return f"{' '.join([x.text for x in self.subj])} | {' '.join([x.text for x in self.pred])} | {' '.join([x.text for x in self.objct])}"

    def __str__(self):
        return f"{' '.join([x.text for x in self.subj])} {' '.join([x.text for x in self.pred])} {' '.join([x.text for x in self.objct])}"


def print_everything(doc):
    """
    Print each token in the doc along with the dependency, text, pos tag, head and childrens.
    Also uses displacy to show in a web browser the dependency tree of the doc
    """
    for token in doc:
        print(token.text, token.dep_, token.head.text, token.head.pos_, [child for child in token.children])
    displacy.serve(doc, style='dep', options = {"collapse_phrases": True, "collapse_punct": True, "distance": 125})

######################
# Sentence functions #
######################

def get_sentences(doc):
    """
    Get a list with the sentences of the input document (spacy).
    """
    sentences = []
    for sente in doc.sents:
        sentences.append(sente)
    return(sentences)

def clean_text(text):
    #remove all the parentheses
    text = re.sub("\([^()]+\) ", "", text)
    # text = re.sub("\([^()]+\)", "", text, 1)
    return(text)

def get_dates_first_sentence(sentence):
    # month, day, year
    date_pattern1 = "(January|Jan|February|Feb|March|Mar|April|Apr|May|May|June|Jun|July|Jul|August|Aug|September|Sep|October|Oct|November|Nov|December|Dec) (\d{1,2}), (\d{4})"
    # day, month, year
    date_pattern2 = "(\d{1,2}) (January|Jan|February|Feb|March|Mar|April|Apr|May|May|June|Jun|July|Jul|August|Aug|September|Sep|October|Oct|November|Nov|December|Dec) (\d{4})"
    first_date = ""
    last_date = ""
    sentence = str(sentence)
    parnth = re.findall("\(.*?\)", sentence)
    if parnth:
        dp1 = re.findall(date_pattern1, sentence)
        dp2 = re.findall(date_pattern2, sentence)
        if dp1:
            if len(dp1) == 1:
                first_date = dp1[0][1] + " " + dp1[0][0] + " " + dp1[0][2]
            elif len(dp1) == 2:
                first_date = dp1[0][1] + " " + dp1[0][0] + " " + dp1[0][2]
                last_date = dp1[1][1] + " " + dp1[1][0] + " " + dp1[1][2]
        elif dp2:
            if len(dp2) == 1:
                first_date = dp2[0][0] + " " + dp2[0][1] + " " + dp2[0][2]
            elif len(dp2) == 2:
                first_date = dp2[0][0] + " " + dp2[0][1] + " " + dp2[0][2]
                last_date = dp2[1][0] + " " + dp2[1][1] + " " + dp2[1][2]

    return first_date, last_date

def get_dates_triples(sentence):
    results = []
    first_date, last_date = get_dates_first_sentence(sentence)
    if first_date:
        #results.append(f"individual born {first_date}")
        results.append(f"individual born {first_date}")
    if last_date:
        #results.append(f"individual death {last_date}")
        results.append(f"individual death {last_date}")
    return results

def get_sentences_by_nverbs(sentences):
    """
    Classifies each sentence from the input list of sentences into simple sentences or complex sentences.
    Simple sentences are those who sentences with just one verb (regular or auxiliary) or 2 verbs (aux + verb)
    Complex sentences are those with multiple verbs in one sentence, usually being clause modifiers
    """
    #sentences = get_sentences(doc)
    simple_sentences = []
    complex_sentences = []
    for s in sentences:
        regular_verbs = 0
        aux_verbs = 0
        mult_verbs = 0
        # Counting verbs
        for token in s:
            if(token.pos == VERB):
                regular_verbs = regular_verbs + 1
            elif(token.pos == AUX):
                aux_verbs = aux_verbs + 1
                if(token.head.pos == VERB):
                    mult_verbs = mult_verbs + 1

        # Classifying verbs into simple or complex sentences
        if(regular_verbs + aux_verbs == 1):
            simple_sentences.append(s)
        elif(regular_verbs == 1 and aux_verbs == 1):
            if(mult_verbs == 1):
                simple_sentences.append(s)
            else:
                complex_sentences.append(s)
        else:
            complex_sentences.append(s)
            
    return simple_sentences, complex_sentences

def get_num_verbs(sentence):
    """
    Get the number of verbs in the input sentence. Precisely returns 1 if the sentence is simple and 2 if the sentence is complex.
    Simple sentences are those who sentences with just one verb (regular or auxiliary) or 2 verbs (aux + verb).
    Complex sentences are those with multiple verbs in one sentence, usually being clause modifiers.
    Similiar to get_sentences_by_nverbs.
    """
    regular_verbs = 0
    aux_verbs = 0
    mult_verbs = 0
    for token in sentence:
        # count verbs
        if(token.pos == VERB):
            regular_verbs = regular_verbs + 1
        elif(token.pos == AUX):
            aux_verbs = aux_verbs + 1
            if(token.head.pos == VERB):
                mult_verbs = mult_verbs + 1

    # 1 regular verb or aux verbs
    if(regular_verbs + aux_verbs == 1):
        return 1
    
    elif(regular_verbs == 1 and aux_verbs == 1):
        if(mult_verbs == 1):
            return 1
        else:
            return 2
    else:
        return 2


def simplify_sentence(complex_sentence):
    """
    Takes a complex sentence as imput and produce a list of simpler sentences of type span.
    The complex sentence is break down into simpler ones by lookin at certain dependency tags in the tokens, 
    these are clausual modifiers or complements.
    """
    # advcl: adverbial clause modifier
    # relcl: relative clause modifier
    # xcomp: open clausal complement 
    # acl: clausal modifier of noun (adjectival clause)
    # ccomp: clausal complement 
    # conj
    result_sentences = [] 
    root_clau = []
    clauses = []
    err = False
    for token in complex_sentence:
        if token.dep_ == "ROOT":
            root_clau.append(token)
        elif token.dep_ in  ["advcl", "relcl", "acl"]:
            clauses.append(token)
        elif token.dep_ == "conj" and token.head.pos == VERB:
            clauses.append(token)

    # Extract main simple sentence from complex sentence (only one root)
    for token in root_clau:
        sent = []
        for token_children in token.subtree:  
            ancestors = [t for t in token_children.ancestors]
            if any([t.dep_ in ["advcl", "acl", "relcl"] for t in ancestors]):
                break
            sent.append(token_children)
        # Make span
        try:
            result_sentences.append(sent[0].doc[sent[0].i : sent[-1].i+1])
        except:
            err = True
    if err:
        return []
    else:
        result_sentences.extend(get_simplified_sents_clauses(clauses))
        return result_sentences

def get_simplified_sents_clauses(clauses):
    """
    Function that takes a list of tokens with a dependency tag of a clause modifier and computes the subtree for each token.
    Then substracts the tokens of other simpler sentences (since the subtree can capture more than one simple sentence)
    Returns a list of simple sentence of type span
    """
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

################################
# Triples extraction functions #
################################

def get_simple_triples(sentence):
    """
    Get the triples from each sentence in <subject, predicate, object> format.
    Firs identify the root verb of the dependency tree and explore each subtrees.
    If a subtree contains any kind of subject, all the subtree will be classified as subject, 
    the same happens with the objects.
    This function only works with simple sentences.
    """
    triples = []
    subjs = []
    objs = []
    preds = []
    root_token = sentence.root
    preds.append(root_token)
    for children in root_token.children:
        if(children.dep_ in ["aux","auxpass"]):
            # children.pos == AUX
            #preds.insert(0,children)
            preds.append(children)
        elif(children.dep_ == "neg"):
            #negative
            #preds.insert(1,children)
            preds.append(children)
        elif(children.dep_ == "xcomp"):
            # consider the prepositions between both verbs (was thought to result)
            xcomp_lefts = [tkn for tkn in children.lefts]
            preds.extend(xcomp_lefts)
            preds.append(children)
        elif children.dep_.find("mod"):
            # advmod
            pass
            #preds.append(children)
        
        preds.sort(key=lambda token: token.i)
        # retrieve subtrees
        is_subj = False
        is_obj = False
        temp_elem = []
        for token_children in children.subtree:
            if token_children in sentence:
                if token_children.dep_.find("subj") == True:
                    is_subj = True
                elif token_children.dep_.find("obj") == True:
                    is_obj = True
                elif token_children.dep_ == "attr":
                    is_obj = True
                if token_children not in preds:
                    temp_elem.append(token_children)
        if is_subj:
            subjs.append(temp_elem)
        elif is_obj:
            objs.append(temp_elem)
    # Build triples
    for s in subjs:
        for o in objs:
            triples.append(Triple(s,preds.copy(),o, sentence))
    return triples

def get_all_triples(sentences):
    """ 
    Extract all the triples from the input list of sentences. Triples can be extracted from simple and complex senteces.
    Returns a list of objects of class Triple.
    """
    triples = []
    for sentence in sentences:
        # complex sentence
        if get_num_verbs(sentence) > 1:
            if USE_COMPLEX_SENTENCES:
                simple_sentences = simplify_sentence(sentence)
                for sent in simple_sentences:
                    tps = get_simple_triples(sent)
                    triples.extend(tps)
        # simple sentence
        else:
            tps = get_simple_triples(sentence)
            triples.extend(tps)
    triples = fix_subj_complex_sentences(triples)
    return triples

##################
# Fixing triples #
##################
def fix_subj_complex_sentences(triples):
    """
    Function that takes the simplified sentences (with a clause modifier in the predicate) and substitutes the subject of the triple with
    the subject or object of the previous triple. This is because usually the simplified sentences has as subject terms like who, that, its, he.
    For example: 
    Original: Alchemy ...... that | was practiced | in China , India , the Muslim world , and Europe
    Results: Alchemy | was practiced | in China , India , the Muslim world , and Europe
    Returns a list of triples
    """
    new_triples = []
    for triple in triples:
        verbs = [tkn for tkn in triple.pred if tkn.pos == VERB]
        verbs = [verb for verb in verbs if (verb.dep_ in ["relcl", "acl", "advcl"] or verb.dep_ == "conj" and verb.head.pos == VERB)]
        previous_triple = []
        if verbs and (previous_triple or new_triples):
            new_triple = triple.get_copy()
            clausule_verb = verbs.pop()
            previous_triple = [t for t in new_triples if clausule_verb.head in t.get_all_tokens()]
            if not previous_triple:
                    previous_triple = new_triples[-1]
            else:
                previous_triple = previous_triple[-1]

            subject = [tkn for tkn in triple.subj if tkn.dep_.find("subj")]
            previous_subject = [tkn for tkn in previous_triple.subj if tkn.dep_.find("subj")]
            previous_object = [tkn for tkn in previous_triple.objct]
            if not subject or not previous_subject:
                new_triples.append(triple)
                continue
            else:
                subject = subject.pop()
                previous_subject = previous_subject.pop()
            
            chains = subject.doc._.coref_chains
            better_subj = chains.resolve(subject)
            if better_subj:
                # coreferee has found coreferences between the current and other triple, check if is the previous one
                if better_subj[0] in previous_triple.subj:
                    new_subj = previous_triple.subj.copy()
                    new_triple.subj = new_subj
                    new_triples.append(new_triple)
                elif better_subj[0] in previous_triple.objct:
                    new_subj = [tkn for tkn in clausule_verb.head.subtree if tkn in previous_triple.objct]
                    new_triple.subj = new_subj
                    new_triples.append(new_triple)
                else:
                    new_triples.append(get_subj_complex_sentence_helper(previous_triple, triple, clausule_verb, previous_subject, subject))
            else:
                new_triples.append(get_subj_complex_sentence_helper(previous_triple, triple, clausule_verb, previous_subject, subject))
        else:
            new_triples.append(triple)
    return new_triples

def get_subj_complex_sentence_helper(previous_triple, triple, clausule_verb, previous_subject, subject):
    """
    Function that takes the simplified sentences (with a clause modifier in the predicate) and substitutes the subject of the triple with
    the subject or object of the previous triple. This is because usually the simplified sentences has as subject terms like who, that, its, he.
    For example: 
    Original: Alchemy ...... that | was practiced | in China , India , the Muslim world , and Europe
    Results: Alchemy | was practiced | in China , India , the Muslim world , and Europe
    Returns a list of triples
    """
    result_triple = triple.get_copy()
    if clausule_verb.dep_ == "acl":
        new_subj = [tkn for tkn in previous_triple.objct]
        #result_triple = Triple(new_subj, triple.pred, triple.objct)
        result_triple.subj = new_subj
    elif clausule_verb.dep_ == "conj":
        new_subj = previous_triple.subj.copy()
        #result_triple = Triple(new_subj, triple.pred, triple.objct)
        result_triple.subj = new_subj
    else:
        if clausule_verb.dep_ == "advcl":
            #print(f"{triple} <> {previous_triple} <> {subject.dep_} <> {previous_subject.dep_}")
            pass
        #relcl, advcl
        if subject.dep_ == "nsubjpass" and previous_subject.dep_ == "nsubj":
            # take the subject of previous triplet as new subject
            new_subj = previous_triple.subj.copy()
            #result_triple = Triple(new_subj, triple.pred, triple.objct)
            result_triple.subj = new_subj
        elif subject.dep != previous_subject.dep:
            #subject.dep_ == "nsubj":
            #take the object of previous triplet as new subject
            new_subj = [tkn for tkn in clausule_verb.head.subtree if tkn in previous_triple.objct]
            #new_subj = [tkn for tkn in previous_triple.objct]
            if not new_subj:
                new_subj = [tkn for tkn in previous_triple.objct]
            #result_triple = Triple(new_subj, triple.pred, triple.objct)
            result_triple.subj = new_subj
        elif subject.dep_ == "nsubj" and previous_subject.dep_ == "nsubj":
            #subject.dep_ == "nsubjpass" or (
            # take the subject of previous triplet as new subject
            new_subj = previous_triple.subj.copy()
            #result_triple = Triple(new_subj, triple.pred, triple.objct)
            result_triple.subj = new_subj
        else:
            result_triple = triple

    return result_triple

def fix_aux_verbs(triples):
    """
    Appends more information to the predicate of the triples with just an auxiliary verb.
    Auxiliary verbs alone do not provide any information, here is an example:
    Original: He | is | a Professor at the Collège de France
    Result: He | is a Professor | at the Collège de France
    Returns a list of triples
    """
    new_triples = []
    for triple in triples:
        # Search triples with just one auxiliary verb
        if (len(triple.pred) == 1) and (triple.pred[0].pos == AUX):

            # retrieve all the tokens from the triple to identify possible candidates
            verb_subtree = [x for x in triple.pred[0].subtree]
            verb_subtree = [item for item in verb_subtree if item in triple.get_all_tokens()]
            verb_mod_explore = []
            for elem in verb_subtree:
                if(elem.dep_ == "attr" and elem.head.pos == AUX):
                    verb_mod_explore.append(elem)
                elif(elem.dep_ == "conj" and elem.head in verb_mod_explore ):
                    verb_mod_explore.append(elem)
            
            verb_mods = []
            for elem in verb_mod_explore:
                verb_mod = []
                explore_childs = [item for item in elem.children if item in triple.get_all_tokens()]
                for child in explore_childs:
                    if child.dep_ in ["det", "amod", "compound"]:
                        verb_mod.append(child)
                verb_mod.append(elem)
                verb_mods.append(verb_mod)

            # Build new object
            if verb_mods:
                if verb_mods[-1][-1] in triple.objct:
                    index = triple.objct.index(verb_mods[-1][-1])+1
                    new_obj = triple.objct[index:]

                    # Fix prepositions
                    if len(new_obj) > 0:
                        if new_obj[0].dep_ == "prep":
                            prep = new_obj.pop(0)
                            for v in verb_mods:
                                if(v[-1].dep_ != "prep"):
                                    v.append(prep)
                    
                    # Build new triples
                    for v in verb_mods:
                        new_triple = triple.get_copy()
                        new_triple.pred = new_triple.pred+v
                        new_triple.objct = new_obj
                        new_triples.append(new_triple)
            else:
                # short frase with no more information (it is in shape)
                new_triples.append(triple) 
        else:
            # If there is no single auxiliary verb append the triple to the new list of triples
            new_triples.append(triple)   
    
    return new_triples

def fix_xcomp_conj(triples):
    """
    Search for triples with a xcomp in the predicate and multiple conjunctions (verbs) in the object part and split them into multiple triples, for example:
    Original: Alchemists attempted to purify, mature, and perfect certain materials.
    Result: Alchemists | attempted to purify | certain materials, Alchemists | attempted to mature | certain materials, Alchemists | attempted to perfect | certain materials, 
    """
    new_triples = []
    for triple in triples:
        # any([tkn for tkn in triple.pred if tkn.dep_ == "xcomp"]) and 
        if any([tkn for tkn in triple.objct if tkn.dep_ == "conj" and (tkn.head.dep_ == "xcomp" and tkn.head in triple.pred)]):
            
            new_obj = triple.objct.copy()
            xcomp = [tkn for tkn in triple.pred if tkn.dep_ == "xcomp"].pop()
            xcomp_pred_idx = triple.pred.index(xcomp)
            conjunctions = [xcomp]
            # Search for conjunction tokens with xcomp or conj parents
            for token in triple.objct:
                if token.dep_ == "conj":
                    if token.head.dep_ in ["conj", "xcomp"]:
                        if token.pos == VERB or token.head in conjunctions:
                            conjunctions.append(token)
                            if token in new_obj:
                                new_obj.remove(token)

            # Remove remaining punct and cc related to conjunctions
            for conjunction in conjunctions:
                for child in conjunction.children:
                    if child.dep_ == "cc" or child.dep_ == "punct":
                        if child in new_obj:
                            new_obj.remove(child)

            # Build new triples
            for conjunction in conjunctions:
                new_triple = triple.get_copy()
                new_triple.pred[xcomp_pred_idx] = conjunction
                new_triple.objct = new_obj
                new_triples.append(new_triple)
        else:
            new_triples.append(triple)
    return new_triples

def append_preps_verbs(triples):
    """
    Search for prepositions in the object part of the triple and appends it to the predicate part of the triple, Here is an example:
    Original: He | was awarded | in 1982
    Result: He | was awarded in | 1982
    Returns a list of triples
    """
    new_triples=[]
    for triple in triples:
        verb = [tkn for tkn in triple.pred if tkn.pos_ == "VERB" or (tkn.pos_ == "AUX" and tkn.dep_ not in ["aux","auxpass"])]
        if verb:
            verb = verb.pop()
            prepositions = [tkn for tkn in verb.children if tkn.dep_ in ["prep","agent"]]
            if prepositions:
                for prep in prepositions:
                    if prep in triple.objct:
                        new_obj = [tkn for tkn in prep.subtree if tkn != prep]
                        new_triple = triple.get_copy()
                        new_triple.pred.append(prep)
                        new_triple.objct = new_obj
                        new_triples.append(new_triple)
            else:
                new_triples.append(triple)
    return new_triples

def split_conjunctions_subjs(triples):
    """
    Search for conjunctions in the subject of each triples and splits in new triples, here is an example:
    Original: Islamic and European alchemists | developed | a basic set of laboratory techniques , theories , and terms
    Result: Islamic alchemists | developed | a basic set of laboratory techniques , theories , and terms and 
    European alchemists | developed | a basic set of laboratory techniques , theories , and terms 
    Returns a list of triples
    """
    new_triples = []
    for triple in triples:
        conjunctions = [token for token in triple.subj if token.dep_ == "conj"]
        main_subject = [token for token in triple.subj if token.dep_.find("subj")]
        if main_subject:
            main_subject = main_subject.pop()
        else:
            # some error when finding the subj in the triple
            new_triples.append(triple)
            continue

        if conjunctions:
            #there is at least one conjunction.
            # First locate the token parent of the first conj and build the first subject
            subjects = []
            new_subject = []
            head_conj = conjunctions[0].head
            if head_conj.dep_ in ["compound", "amod", "nummod", "nmod", "advmod", "npadvmod"]:
                ancestors = [tkn for tkn in head_conj.ancestors]
                ancestors.insert(0,head_conj)
                if main_subject in ancestors:
                    subj_idx = ancestors.index(main_subject)+1
                    new_subject.extend(ancestors[:subj_idx])
                else:
                    continue
            else:
                # head_conj probably the subj
                new_subject.append(head_conj)
            subjects.append(new_subject)

            for conjunction in conjunctions:
                new_subject = []
                #if conjunction.head.dep_ == "amod":
                if conjunction.head.dep_ in ["compound", "amod", "nummod", "nmod", "advmod", "npadvmod"]:
                    # In case that the parent is amod, the child is also amod
                    # search the noun of the amod and build new triples
                    parent_mod = conjunction.head
                    new_subject.extend([conjunction,parent_mod.head])
                    #new_object.extend([parent_mod,parent_mod.head])
                    subjects.append(new_subject)

                else:
                    # parent is nsubj
                    for child in conjunction.children:
                        if child.dep_ in ["compound", "amod", "nummod", "nmod", "advmod", "npadvmod"]:
                            new_subject.append(child)
                    new_subject.append(conjunction)
                    subjects.append(new_subject)


            # Build triples
            for s in subjects:
                new_triple = triple.get_copy()
                new_triple.subj = s
                new_triples.append(new_triple)
        else:
            # There are no conjunctions, we store the triple without any operations
            new_triples.append(triple)
    return new_triples

def split_conjunctions_obj(triples):
    """
    Search for conjunctions in the object of each triples and splits in new triples, here is an example:
    Original: Alchemy | was practiced | in China , India , the Muslim world , and Europ
    Result: Alchemy | was practiced in | China , Alchemy | was practiced in | India ,
     Alchemy | was practiced in | the Muslim world , Alchemy | was practiced in | Europe
    Returns a list of triples
    """
    new_triples = []
    for triple in triples:
        conjunctions = [token for token in triple.objct if token.dep_ == "conj"]
        
        if conjunctions:
            #there is at least one conjunction.
            # First locate the token parent of the first conj and build the first object
            head_conj = conjunctions[0].head
            if head_conj in triple.objct:
                head_conj_idx = triple.objct.index(head_conj)
                main_part = triple.objct[:head_conj_idx]
                objects = []
                first_object = main_part.copy()
                # check if parent token (conj origin) have any modifier (compound or amod)
                if main_part:
                    if main_part[-1].dep_ in ["compound", "amod"] and head_conj.is_ancestor(main_part[-1]):
                        modifiers = [tkn for tkn in main_part[-1].subtree]
                        main_part = [elem for elem in main_part if elem not in modifiers]
                        first_object = main_part.copy()
                        first_object.extend(modifiers)

                first_object.append(head_conj)
                objects.append(first_object)

                for conjunction in conjunctions:
                    new_object = main_part.copy()
                    if conjunction.head.dep_ == "amod":
                        # In case that the parent is amod, the child is also amod
                        # search the noun of the amod and build new triples
                        # maybe check not the parent but the whole ancestors?
                        parent_mod = conjunction.head
                        new_object.extend([conjunction,parent_mod.head])
                        #new_object.extend([parent_mod,parent_mod.head])
                        objects.append(new_object)
                    else:
                        for child in conjunction.children:
                            if child.dep_ in ["amod", "compound"]:
                                new_object.append(child)
                        new_object.append(conjunction)
                        objects.append(new_object)

                # Build triples
                for o in objects:
                    new_triple = triple.get_copy()
                    new_triple.objct = o
                    new_triples.append(new_triple)
            else:
                # The conjunction parent is the verb or some other token outside the object part of the tripelt
                new_triples.append(triple)
        else:
            # There are no conjunctions, we store the triple without any operations
            new_triples.append(triple)
    return new_triples

def swap_subjects_correferences(triples, chains):
    """
    Description to do
    """
    new_triples = []
    for triple in triples:
        subj = triple.subj.copy()
        better_subj = None
        for token in subj:
            better_subj = chains.resolve(token)
            if better_subj:
                break
        if better_subj:
            better_subj = [tkn for tkn in better_subj[0].subtree]
            new_triple = triple.get_copy()
            new_triple.subj = better_subj
            new_triples.append(new_triple)
        else:
            # there arent correferences
            new_triples.append(triple)

    return new_triples

###############
# Text to RDF #
###############

def get_annotated_text_dict(text, service_url=SPOTLIGHT_ONLINE_API, confidence=0.3, support=0, dbpedia_only = True):
    """
    Function that query's the dbpedia spotlight api with the document text as input. Confidence level is the
    confidence score for disambiguation / linking and support is how prominent is this entity in Lucene Model, i.e. number of inlinks in Wikipedia.
    Returns a dictionary with term-URI and a dictionary with term-types (from an ontology)
    """
    headerinfo = {'Accept': 'application/json'}
    parameters = {'text': text, 'confidence': confidence, 'support': support}
    term_URI_dict = {}
    term_types_dict = {}
    try:
        if "localhost" in service_url:
            resp = requests.post(service_url, data=parameters, headers=headerinfo)
        else:
            resp = requests.get(service_url, params=parameters, headers=headerinfo)
    except:
        print("Error at dbpedia spotlight post/get")
        return None

    if resp.status_code != 200:
        print(f"error, status code{resp.status_code}")
        return None
    else:
        
        decoded = json.loads(resp.text)

        if 'Resources' in decoded:
            for dec in decoded['Resources']:
                term_URI_dict[dec['@surfaceForm'].lower()] = dec['@URI'].lower()
                term_types_dict[dec['@URI'].lower()] = dec['@types'].lower().split(",")

            if dbpedia_only:
                for key,value in term_types_dict.items():
                    value = [x.replace('dbpedia:', 'https://dbpedia.org/ontology/') for x in value if "dbpedia:" in x]
                    term_types_dict[key] = value

    return term_URI_dict, term_types_dict

def load_dbo_graph(dbo_path):
    """ Return the ontology as a rdflib graph """
    g = Graph()
    g.parse(dbo_path)
    return g

def load_lexicalization_table(lex_path):
    """ Return the lexicalization table as a python dict of dics (verbs and prepositions, classes) """
    with open(lex_path) as json_file:
        lexicalization_table = json.load(json_file)
    return lexicalization_table

def replace_text_URI(triples, term_URI_dict, term_types_dict, prop_lex_table, cla_lex_table, dbo_graph):
    """
    Maybe this function should be inside the triple class
    """
    new_triples = []
    for triple in triples:
        subj = [x for x in triple.subj if x.dep_ != "det"]
        subj = ' '.join([x.text.lower() for x in subj])
        orginal_pred = ' '.join([x.text.lower() for x in triple.pred])
        objct = ' '.join([x.text.lower() for x in triple.objct])
        
        verb = [tkn for tkn in triple.pred if tkn.pos_ == "VERB" or (tkn.pos_ == "AUX" and tkn.dep_ not in ["aux","auxpass"])].pop()
        verb = str(verb.lemma_)
        prep = [tkn.text for tkn in triple.pred if tkn.dep_ == "prep"]
        if prep:
            prep = prep.pop()
            prep = prep.lower()
        else:
            prep = DEFAULT_VERB

        # NER the subject
        s_candidates = []
        keys = []
        for key in term_URI_dict.keys():
            if key in subj.lower():
                s_candidates.append(term_URI_dict[key])
                keys.append(key)

        # removing some subjects (not definitive)
        if len(keys) > 1:
            candidate = [b for a,b in zip(keys, s_candidates) if " " in a]
            if candidate:
                s_candidates = [candidate.pop()]
            else:
                s_candidates = [s_candidates.pop()]

        if verb == "be" and prep == DEFAULT_VERB:
            # the case of the verb to be has to be treated different from the rest
            objct = get_dbo_class(objct, cla_lex_table)
            o_candidates = [objct]
            pred = prop_lex_table[verb][prep]
        else:
            # NER the object
            o_candidates = []
            for key in term_URI_dict.keys():
                if key in objct.lower():
                    o_candidates.append(term_URI_dict[key])

            # Lexicalization predicate        
            if verb in prop_lex_table:
                if prep in prop_lex_table[verb]:
                    if prop_lex_table[verb][prep] == UNKOWN_VALUE:
                        pred = prop_lex_table[verb][DEFAULT_VERB]
                    else:
                        pred = prop_lex_table[verb][prep]

                else:
                    pred = prop_lex_table[verb][DEFAULT_VERB]
            else:
                pred = Literal(orginal_pred)
            
        # Build triple

        for s in s_candidates:
            for o in o_candidates:
                if isinstance(pred,list):
                    # temporal fix, to be changed
                    # pred = pred.pop()
                    pred = get_best_candidate(s, o, pred, term_types_dict, dbo_graph)
                else:
                    if not isinstance(pred, Literal):
                        pred = URIRef(pred)
                if not isinstance(o, Literal):
                    o = URIRef(o)

                new_triple = triple.get_copy()
                new_triple.set_rdf_triples(URIRef(s),pred,o)
                new_triples.append(new_triple)

    return new_triples

def get_best_candidate(subj, objct, candidates, term_types_dict, dbo_graph):

    # get list of classes of elems

    subj = [URIRef(x) for x in term_types_dict[subj]]
    objct = [URIRef(x) for x in term_types_dict[objct]] 

    scores = []
    for candidate in candidates:
        score = 0
        candidate = URIRef(candidate)
        p_range = dbo_graph.value(subject=candidate, predicate=RDFS.range)
        p_domain = dbo_graph.value(subject=candidate, predicate=RDFS.domain)
        if p_domain in subj:
            score = score + 1
        elif p_range in objct:
            score = score + 1
        scores.append(score)

    best_score = max(scores)
    result = candidates[scores.index(best_score)]
    return URIRef(result)
    
def get_dbo_class(objct, cla_lex_table):
    """ Function that returns a dbo class given a text, for the to be case """
    objct = objct.lower()
    if objct in cla_lex_table.keys():
        return URIRef(cla_lex_table[objct])
    else:
        candidates = []
        temp_obj = objct.split(" ")
        for k in cla_lex_table.keys():
            if k in temp_obj:
                candidates.append(k)
        # strategy to select best candidate
        if candidates:
            key = candidates.pop()
            result = cla_lex_table[key]
            return URIRef(result)
        else:
            return Literal(objct)

def build_result_graph(triples):
    """ Builds a rdf graph with the result triples """

    g = Graph()
    for triple in triples:
        triple.get_rdf_triple()
        g.add((triple.subj_rdf, triple.pred_rdf, triple.objct_rdf))
    print(g.serialize(format='ttl'))

# Main pipeline
def pipeline(nlp, document, dbo_graph, prop_lex_table, cla_lex_table):
    """ Main sequence of steps to process certain input text into triples. """
    text = clean_text(document)
    #d1,d2 = get_dates_first_sentence(document)
    doc = nlp(text)
    sentences = get_sentences(doc)
    triples = get_all_triples(sentences)
    triples = fix_xcomp_conj(triples)
    # triples = fix_aux_verbs(triples)
    triples = append_preps_verbs(triples)
    triples = split_conjunctions_subjs(triples)
    triples = split_conjunctions_obj(triples)
    triples = swap_subjects_correferences(triples, doc._.coref_chains)
    try:
        term_URI_dict, term_types_dict = get_annotated_text_dict(text, service_url=SPOTLIGHT_LOCAL_URL)
    except:
        return [],[],[]
    rdf_triples = replace_text_URI(triples, term_URI_dict, term_types_dict, prop_lex_table, cla_lex_table, dbo_graph)
    print_rdf_results(rdf_triples)
    #build_result_graph(rdf_triples)
    
    return sentences, triples, rdf_triples

def print_rdf_results(triples):
    """ Print the final result: Original sentence, text triples and rdf triples"""
    if triples:
        sent = triples[0].sent
        print("-"*50)
        print(f"**{sent}**")
        print("\n")
        for t in triples:
            if t.sent != sent:
                sent = t.sent
                print("\n")
                print("-"*50)
                print(f"**{sent}**")
                print("\n")
            print(t.__repr__())
            print(t.get_rdf_triple())

def print_triples(text, triples):
    print(text)
    print("-"*64)
    print("\n"*2)
    for triple in triples:
        print(triple.__repr__())
        print("*"*64)
    print("\n"*2)

def get_missclassified_objects(rdf_triples):
    be = URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type")
    errors = []

    for triple in rdf_triples:
        if triple.pred_rdf == be:
            if isinstance(triple.objct_rdf, Literal):
                errors.append(triple)
    return errors

def get_preds_literals(rdf_triples):
    errors = []

    for triple in rdf_triples:
        if isinstance(triple.pred_rdf, Literal):
                errors.append(triple)
    return errors

def count_literals(rdf_triples):
    be = URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type")
    preds = 0
    objcts = 0

    for triple in rdf_triples:
        if isinstance(triple.pred_rdf, Literal):
            preds += 1
        if isinstance(triple.objct_rdf, Literal) and triple.pred_rdf != be:
            objcts +=1
    return preds, objcts

def count_tobe(rdf_triples):
    be = URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type")
    count = 0
    for triple in rdf_triples:
        if triple.pred_rdf == be:
            count += 1
    return count

def main():
    # Load dependency model and add coreferee support
    nlp = spacy.load("en_core_web_trf")
    nlp.add_pipe('coreferee')

    # Load datastructures
    prop_lex_table = load_lexicalization_table(PROP_LEXICALIZATION_TABLE)
    cla_lex_table = load_lexicalization_table(CLA_LEXICALIZATION_TABLE)
    dbo_graph = load_dbo_graph(DBPEDIA_ONTOLOGY)
#    df = pd.read_csv(DATASET_PATH)
#    test_examples = df["abstract"]
    # Initialize counters
    nt_count = 0
    rt_count = 0
    s_sentences_count = 0
    c_senteces_count = 0
    total_sentences = 0
    literals_pred = 0
    literals_objct = 0
    tobe_count = 0
    errors_be = []
    errors_pred = []
    elap_time = 0
    num_abstracts = len(test_examples)
    
    for example in test_examples:
        start = time.time()

        sentences, normal_triples, rdf_triples = pipeline(nlp, example, dbo_graph ,prop_lex_table, cla_lex_table)
        if sentences == [] and normal_triples == [] and rdf_triples == []:
            #error
            num_abstracts -= 1
        else:
            nt_count += len(normal_triples)
            rt_count += len(rdf_triples)
            for sentence in sentences:
                if get_num_verbs(sentence) > 1:
                    c_senteces_count += 1
                else:
                    s_sentences_count += 1
            total_sentences += len(sentences)
            errors_be.extend(get_missclassified_objects(rdf_triples))
            errors_pred.extend(get_preds_literals(rdf_triples))
            l_pred, l_objct = count_literals(rdf_triples)
            tobe_count += count_tobe(rdf_triples)
            literals_pred += l_pred
            literals_objct += l_objct
            end = time.time()
            elap_time += end - start

    print(f"Num of abstracts {num_abstracts}")
    print(f"Simple sentences: {s_sentences_count}, from each text avg of {s_sentences_count/num_abstracts} simple sentences")
    print(f"Complex sentences: {c_senteces_count}, from each text avg of {c_senteces_count/num_abstracts} complex sentences")
    print(f"Total number of sentences {total_sentences}")
    print(f"Number of normal text triples {nt_count}, from each text avg of {nt_count/num_abstracts} triplets")
    print(f"Number of RDF text triples {rt_count}, from each text avg of {rt_count/num_abstracts} triplets")
    print(f"Triplets with tobe as pred {tobe_count}")
    print(f"Number of errors with the verb to be (literals as object): {len(errors_be)}")
    print(f"Number of predicate as literals: {literals_pred}")
    print(f"Number of literals as objects {literals_objct}")
    print(f"Total num of triplets containing a literal {literals_pred+literals_objct} + the to be cases {len(errors_be)}")
    print(f"total time: {elap_time}, avg time {elap_time/num_abstracts}")
    print(errors_be[:5])
    
    '''textfile = open("results/errors_pred.txt", "w")
    for element in errors_pred:
        textfile.write(element.__repr__())
        textfile.write("\n")
    textfile.close()'''
#    exit()

    for t in rdf_triples:
        # debug
        print(t.subj_rdf, '|', t.pred_rdf, '|', t.objct_rdf)


if __name__ == "__main__":
    main()


