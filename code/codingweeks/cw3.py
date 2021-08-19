"""
Coding week 3
Author: Fernando Casabán Blasco
"""

# load all examples
# trim better the phrases
# subjs modifiers as new triplets red ballon | whatever | whatever --> ballon | property | red

# \(.*?\)
# (August 4, 1910 – March 19, 1968)
# (February 11, 1975 – May 21, 2010)
# (born January 7, 1981)
# (植田 憲一, Ueda Ken'ichi; born on October 22, 1946)
# (born 17 February 1947)
# (1 March 1913 – 31 May 1991) 
# (24 December 1825 – 13 October 1903)
# (born 15 February 1981)
# (born April 27, 1957)
# matches = re.findall('(\d{2}[\/ ](\d{2}|January|Jan|February|Feb|March|Mar|April|Apr|May|May|June|Jun|July|Jul|August|Aug|September|Sep|October|Oct|November|Nov|December|Dec)[\/ ]\d{2,4})', string)

from os import PRIO_PGRP, pipe
import spacy
import re
from spacy.symbols import nsubj, VERB, AUX, PUNCT
from spacy import displacy
from spacy.matcher import Matcher
import pandas as pd

class Document:
    def __init__(self, triples):
        self.triples = triples

class Triple:
    def __init__(self, subj, pred, obj):
        self.subj = subj
        self.pred = pred
        self.obj = obj
    
    def __repr__(self):
        return f"{' '.join(self.subj)} | {' '.join(self.pred)} | {' '.join(self.obj)}"

    def __str__(self):
        return f"{' '.join(self.subj)} {' '.join(self.pred)} {' '.join(self.obj)}"

t = Triple(["He"], ["was", "awarded", "in"], ["1982"])
print(repr(t))   #Vector3([1,2,3])
print(str(t))   #x:1, y:2, z:3

test_examples = [
    "Alchemy (from Arabic: al-kīmiyā; from Ancient Greek: khumeía) is an ancient branch of natural philosophy, a philosophical and protoscientific tradition that was historically practiced in China, India, the Muslim world, and Europe. In its Western form, it is first attested in a number of pseudepigraphical texts written in Greco-Roman Egypt during the first few centuries CE.Alchemists attempted to purify, mature, and perfect certain materials. Common aims were chrysopoeia, the transmutation of \"base metals\" (e.g., lead) into \"noble metals\" (particularly gold); the creation of an elixir of immortality; and the creation of panaceas able to cure any disease. The perfection of the human body and soul was thought to result from the alchemical magnum opus (\"Great Work\"). The concept of creating the philosophers' stone was variously connected with all of these projects.Islamic and European alchemists developed a basic set of laboratory techniques, theories, and terms, some of which are still in use today. However, they did not abandon the ancients' belief that everything is composed of four elements, and they tended to guard their work in secrecy, often making use of cyphers and cryptic symbolism. In Europe, the 12th-century translations of medieval Islamic works on science and the rediscovery of Aristotelian philosophy gave birth to a flourishing tradition of Latin alchemy. This late medieval tradition of alchemy would go on to play a significant role in the development of early modern science (particularly chemistry and medicine).Modern discussions of alchemy are generally split into an examination of its exoteric practical applications and its esoteric spiritual aspects, despite criticisms by scholars such as Eric J. Holmyard and Marie-Louise von Franz that they should be understood as complementary. The former is pursued by historians of the physical sciences, who examine the subject in terms of early chemistry, medicine, and charlatanism, and the philosophical and religious contexts in which these events occurred. The latter interests historians of esotericism, psychologists, and some philosophers and spiritualists. The subject has also made an ongoing impact on literature and the arts.",
    "A, or a, is the first letter and the first vowel letter of the modern English alphabet and the ISO basic Latin alphabet. Its name in English is a (pronounced ), plural aes. It is similar in shape to the Ancient Greek letter alpha, from which it derives. The uppercase version consists of the two slanting sides of a triangle, crossed in the middle by a horizontal bar. The lowercase version can be written in two forms: the double-storey a and single-storey ɑ. The latter is commonly used in handwriting and fonts based on it, especially fonts intended to be read by children, and is also found in italic type.In the English grammar, \"a\", and its variant \"an\", are indefinite articles.",
    "Analysis of variance (ANOVA) is a collection of statistical models and their associated estimation procedures (such as the \"variation\" among and between groups) used to analyze the differences among means. ANOVA was developed by the statistician Ronald Fisher. ANOVA is based on the law of total variance, where the observed variance in a particular variable is partitioned into components attributable to different sources of variation. In its simplest form, ANOVA provides a statistical test of whether two or more population means are equal, and therefore generalizes the t-test beyond two means.",
    "Allan Dwan (born Joseph Aloysius Dwan; 3 April 1885 – 28 December 1981) was a pioneering Canadian-born American motion picture director, producer, and screenwriter.",
    "Animalia is an illustrated children's book by Graeme Base. It was originally published in 1986, followed by a tenth anniversary edition in 1996, and a 25th anniversary edition in 2012. Over four million copies have been sold worldwide. A special numbered and signed anniversary edition was also published in 1996, with an embossed gold jacket.",
    "Anarchism is a political philosophy and movement that is sceptical of authority and rejects all involuntary, coercive forms of hierarchy. Anarchism calls for the abolition of the state, which it holds to be undesirable, unnecessary, and harmful. As a historically far-left movement, it is usually described alongside libertarian Marxism as the libertarian wing (libertarian socialism) of the socialist movement and has a strong historical association with anti-capitalism and socialism.The history of anarchy goes back to prehistory, when humans arguably lived in anarchic societies long before the establishment of formal states, realms or empires. With the rise of organised hierarchical bodies, scepticism toward authority also rose, but it was not until the 19th century that a self-conscious political movement emerged. During the latter half of the 19th and the first decades of the 20th century, the anarchist movement flourished in most parts of the world and had a significant role in workers' struggles for emancipation. Various anarchist schools of thought formed during this period. Anarchists have taken part in several revolutions, most notably in the Spanish Civil War, whose end marked the end of the classical era of anarchism. In the last decades of the 20th and into the 21st century, the anarchist movement has been resurgent once more.Anarchism employs a diversity of tactics in order to meet its ideal ends which can be broadly separated into revolutionary and evolutionary tactics. There is significant overlap between the two which are merely descriptive. Revolutionary tactics aim to bring down authority and state, having taken a violent turn in the past. Evolutionary tactics aim to prefigure what an anarchist society would be like. Anarchist thought, criticism and praxis have played a part in diverse areas of human society. Criticisms of anarchism include claims that it is internally inconsistent, violent, or utopian.",
    "Agricultural science is a broad multidisciplinary field of biology that encompasses the parts of exact, natural, economic and social sciences that are used in the practice and understanding of agriculture. Professionals of the agricultural science are called agricultural scientists or agriculturists.",
    "Albedo (pronounced ; Latin: albedo, meaning 'whiteness') is the measure of the diffuse reflection of solar radiation out of the total solar radiation and measured on a scale from 0, corresponding to a black body that absorbs all incident radiation, to 1, corresponding to a body that reflects all incident radiation.Surface albedo is defined as the ratio of radiosity Je to the irradiance Ee (flux per unit area) received by a surface. The proportion reflected is not only determined by properties of the surface itself, but also by the spectral and angular distribution of solar radiation reaching the Earth's surface. These factors vary with atmospheric composition, geographic location and time (see position of the Sun). While bi-hemispherical reflectance is calculated for a single angle of incidence (i.e., for a given position of the Sun), albedo is the directional integration of reflectance over all solar angles in a given period. The temporal resolution may range from seconds (as obtained from flux measurements) to daily, monthly, or annual averages.Unless given for a specific wavelength (spectral albedo), albedo refers to the entire spectrum of solar radiation. Due to measurement constraints, it is often given for the spectrum in which most solar energy reaches the surface (between 0.3 and 3 μm). This spectrum includes visible light (0.4–0.7 μm), which explains why surfaces with a low albedo appear dark (e.g., trees absorb most radiation), whereas surfaces with a high albedo appear bright (e.g., snow reflects most radiation).Albedo is an important concept in climatology, astronomy, and environmental management (e.g., as part of the Leadership in Energy and Environmental Design (LEED) program for sustainable rating of buildings). The average albedo of the Earth from the upper atmosphere, its planetary albedo, is 30–35% because of cloud cover, but widely varies locally across the surface because of different geological and environmental features.The term albedo was introduced into optics by Johann Heinrich Lambert in his 1760 work Photometria.",
    "The Austroasiatic languages , also known as Mon–Khmer , are a large language family of Mainland Southeast Asia, also scattered throughout parts of India, Bangladesh, Nepal, and southern China. There are around 117 million speakers of Austroasiatic languages. Of these languages, only Vietnamese, Khmer and Mon have a long-established recorded history and only Vietnamese and Khmer have official status as modern national languages (in Vietnam and Cambodia, respectively). The Mon language is a recognized indigenous language in Myanmar and Thailand. In Myanmar, the Wa language is the de facto official language of Wa State. Santali is one of the 22 scheduled languages of India. The rest of the languages are spoken by minority groups and have no official status.Ethnologue identifies 168 Austroasiatic languages. These form thirteen established families (plus perhaps Shompen, which is poorly attested, as a fourteenth), which have traditionally been grouped into two, as Mon–Khmer and Munda. However, one recent classification posits three groups (Munda, Nuclear Mon-Khmer and Khasi–Khmuic), while another has abandoned Mon–Khmer as a taxon altogether, making it synonymous with the larger family.Austroasiatic languages have a disjunct distribution across Southeast Asia and parts of India, Bangladesh, Nepal and East Asia, separated by regions where other languages are spoken. They appear to be the extant autochthonous languages of Mainland Southeast Asia (excluding the Andaman Islands), with the neighboring Kra–Dai, Hmong-Mien, Austronesian, and Sino-Tibetan languages being the result of later migrations.",
    "Barack Hussein Obama II is an American politician who is the 44th and current President of the United States. He is the first African American to hold the office and the first president born outside the continental United States. Born in Honolulu, Hawaii, Obama is a graduate of Columbia University and Harvard Law School, where he was president of the Harvard Law Review. He was a community organizer in Chicago before earning his law degree. He worked as a civil rights attorney and taught constitutional law at the University of Chicago Law School between 1992 and 2004. While serving three terms representing the 13th District in the Illinois Senate from 1997 to 2004, he ran unsuccessfully in the Democratic primary for the United States Hou",
    "Elon Reeve Musk (/ˈiːlɒn ˈmʌsk/; born June 28, 1971) is a South African-born Canadian-American business magnate, investor, engineer and inventor. He is the founder, CEO, and CTO of SpaceX; co-founder, CEO, and product architect of Tesla Motors; co-founder and chairman of SolarCity; co-chairman of OpenAI; co-founder of Zip2; and founder of X.com which merged with PayPal of Confinity. As of June 2016, he has an estimated net worth of US$12.7 billion, making him the 83rd wealthiest person in the world. Musk has stated that the goals of SolarCity, Tesla Motors, and SpaceX revolve around his vision to change the world and humanity. His goals include reducing global warming through sustainable energy production and consumption, and reducing the \"risk of human extinction\" by \"making life multiplanetary\" by setting up a human colony on Mars. In addition to his primary business pursuits, he has also envisioned a high-speed transportation system known as the Hyperloop, and has proposed a VTOL supersonic jet aircraft with electric fan propulsion, known as the Musk electric jet.",
    "Anton Drexler (13 June 1884 – 24 February 1942) was a German far-right political leader of the 1920s who was instrumental in the formation of the pan-German and anti-Semitic German Workers' Party (Deutsche Arbeiterpartei – DAP), the antecedent of the Nazi Party (Nationalsozialistische Deutsche Arbeiterpartei – NSDAP). Drexler served as mentor to Adolf Hitler during his early days in politics.",
    "Alain Connes (French: [alɛ̃ kɔn]; born 1 April 1947) is a French mathematician, and a theoretical physicist, known for his contributions to the study of operator algebras and noncommutative geometry. He is a Professor at the Collège de France, IHÉS, Ohio State University and Vanderbilt University. He was awarded the Fields Medal in 1982."
]

def get_sentences(doc):
    # Extract the sentences
    sentences = []
    for sente in doc.sents:
        sentences.append(sente)
    return(sentences)

def sentences_1_verb(sentences):
    #sentences = get_sentences(doc)
    results = []
    for s in sentences:
        regular_verbs = 0
        aux_verbs = 0
        mult_verbs = 0
        for token in s:
            if(token.pos == VERB):
                regular_verbs = regular_verbs + 1
            elif(token.pos == AUX):
                aux_verbs = aux_verbs + 1
                if(token.head.pos == VERB):
                    mult_verbs = mult_verbs + 1
        if(regular_verbs + aux_verbs == 1):
            results.append(s)
        elif(regular_verbs == 1 and aux_verbs == 1):
            if(mult_verbs == 1):
                results.append(s)

    return results

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
        results.append(f"individual born {first_date}")
    if last_date:
        results.append(f"individual death {last_date}")
    return results

def get_triples(document):
    triples = []
    for sentence in document:
        subjs = []
        objs = []
        preds = []
        for token in sentence:
            #if(token.pos == VERB or token.pos == AUX):
            if(token.dep_ == "ROOT"):
                pred = token.text
                preds.append(token)
                for children in token.children:
                    if(children.pos == AUX):
                        #auxiliary passive
                        preds.insert(0,children)
                    #    pred = pred + " " + children.text
                    # retrieve subtrees
                    is_subj = False
                    is_obj = False
                    temp_elem = []
                    for token_children in children.subtree:
                        if(token_children.dep_.find("subj")==True):
                            is_subj = True
                        elif(token_children.dep_.find("obj")==True ):
                            is_obj = True
                        elif(token_children.dep_ == "attr"):
                            is_obj = True
                        #if(token_children.pos != PUNCT and token_children.dep_ != "cc"):
                        temp_elem.append(token_children)
                    if(is_subj):
                        subjs.append(temp_elem)
                    elif(is_obj):
                        objs.append(temp_elem)
                    else:
                        pass
        for s in subjs:
            for o in objs:
                triples.append([s,preds.copy(),o])
                #print(f"{s.text}|{pred.text}|{o.text}")
    return triples

def append_preps_verbs(triples):
    for triple in triples:
        #print(triple[2][0].dep_, triple[2][0].pos_)
        if len(triple[2])>0:
            if(triple[2][0].dep_ == "prep" or triple[2][0].dep_ == "agent"):
                triple[1].append(triple[2].pop(0))
    return triples

def split_conjunctions_subjs(triples):
    new_triples = []
    for triple in triples:
        for token in triple[0]:
            if token.dep_ == "conj":
                #new_subjs.append(token)
                new_triples.append([[token], triple[1], triple[2]])
                triple[0].remove(token)
                #remove token
            elif token.dep_ == "punct" or token.dep_ == "cc":
                triple[0].remove(token)
    for t in new_triples:
        triples.append(t)
    return triples

def split_conjunctions_obj(triples):
    new_triples = []
    objs = []
    for triple in triples:
        obj = []
        for token in triple[2]:
            if token.dep_ == "cc" or token.dep_ == "punct" :
                objs.append(obj)
                obj = []
            else:
                obj.append(token)
        if objs:
            for o in objs:
                new_triples.append([triple[0],triple[1],o])
            # remove old triples
            triples.remove(triple)

    #append new triples
    for t in new_triples:
        triples.append(t)
    return triples

def fix_aux_verbs(triples):
    new_triples = []
    for triple in triples:
        # if there is only one verb
        if len(triple[1]) == 1:
            # if there is only one auxiliary verb
            if triple[1][0].pos == AUX:
                # retrieve all the tokens to identify possible candidates
                verb_subtree = [x for x in triple[1][0].subtree]
                verb_mod_explore = []
                for elem in verb_subtree:
                    if(elem.dep_ == "attr" and elem.head.pos == AUX):
                        verb_mod_explore.append(elem)
                    elif(elem.dep_ == "conj" and elem.head in verb_mod_explore ):
                        verb_mod_explore.append(elem)
                
                verb_mods = []
                for elem in verb_mod_explore:
                    verb_mod = []
                    for child in elem.children:
                        if(child.dep_ != "cc" and child.dep_ != "conj" and child.dep_ != "prep"):
                            verb_mod.append(child)
                    verb_mod.append(elem)
                    verb_mods.append(verb_mod)

                # new object
                if(verb_mods[-1][-1] in triple[2]):
                    index = triple[2].index(verb_mods[-1][-1])+1
                    new_obj = triple[2][index:]

                    # Fix prepositions
                    if len(new_obj) > 0:
                        if new_obj[0].dep_ == "prep":
                            prep = new_obj.pop(0)
                            for v in verb_mods:
                                if(v[-1].dep_ != "prep"):
                                    v.append(prep)
                    
                    # new triples
                    for v in verb_mods:
                        new_triples.append([triple[0],triple[1]+v,new_obj])

                    # remove old triples
                    triples.remove(triple)
            
    #append new triples
    for t in new_triples:
        triples.append(t)
    return triples
                
def print_triples(triples):
    for triple in triples:
        s = [x.text for x in triple[0]]
        p = [x.text for x in triple[1]]
        o = [x.text for x in triple[2]]
        print(f"{' '.join(s)} | {' '.join(p)} | {' '.join(o)}")

def pipeline(t, nlp):
    doc = nlp(t)
    sentences = get_sentences(doc)
    dates_triples = get_dates_triples(sentences[0])
    sentences = sentences_1_verb(sentences)
    print(sentences)
    #ncs(sentences)
    #return
    triples = get_triples(sentences)
    #print(triples)

    triples = fix_aux_verbs(triples)
    #print(triples)

    triples = append_preps_verbs(triples)
    #print(triples)

    triples = split_conjunctions_subjs(triples)
    #print(triples)

    triples = split_conjunctions_obj(triples)
    #print(triples)
    print_triples(triples)

    #print(dates_triples)
    #split_conjunctions_obj
def ncs(sentences):
    for s in sentences:
        for chunk in s.noun_chunks:
            print(chunk.text, chunk.root.text, chunk.root.dep_,
            chunk.root.head.text)

def main():
    nlp = spacy.load("en_core_web_sm")
    #nlp = spacy.load("en_core_web_trf")
    # preps after tripoes
    #pipeline(test_examples[12], nlp)
    #exit()
    for t in test_examples:
        pipeline(t,nlp)
        print("---"*50)
    exit()
    doc = nlp(t)
    sentences = get_sentences(doc)
    dates_triples = get_dates_triples(sentences[0])
    print(dates_triples)
    sentences = sentences_1_verb(sentences)
    print(sentences)
    print(get_triples(sentences))
    

    #print(get_dates_first_sentence(get_sentences(doc)[0]))
    #for token in nlp("Alain Connes is a French mathematician, and a theoretical physicist, known for his contributions to the study of operator algebras and noncommutative geometry."):
    #    print(token.text, token.dep_)

    
if __name__ == "__main__":
    main()
