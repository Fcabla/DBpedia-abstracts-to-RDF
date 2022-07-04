import os
import random
import spacy
from spacy import displacy

os.chdir('../../../long abstracts/')
WORD = 'where'
NUMBER_OF_SENTENCES = 100

'''with open("selected_abstracts.txt", "w", encoding="utf8") as file_w:
    with open("long-abstracts_lang=en.ttl", encoding="utf8") as file:
        number_line_infile = 1
        selected_sentences = 0
        for line in file:
            pos_start = line.find("/abstract> \"")
            pos_end = line.find("@en")
            sentence = line[pos_start+12:pos_end-1]
            if sentence:
                if sentence.find(f" {WORD} ") > 0:
                    sentence = '[' + str(number_line_infile) + '] ' + sentence + '\n'
                    file_w.write(sentence)
                    selected_sentences = selected_sentences + 1
            number_line_infile = number_line_infile + 1
            if (number_line_infile % 100000) == 0:
                print('=', end='')
    file.close()
file_w.close()
print('\nLeídos ', number_line_infile, 'abstracts')
print('Seleccionados ', selected_sentences, 'abstracts')

test_data = random.sample(range(1, selected_sentences), NUMBER_OF_SENTENCES)
test_data.sort()
with open(f"{WORD.upper()}_test_data.txt", "w", encoding="utf8") as file_w:
    with open("selected_abstracts.txt", encoding="utf8") as file:
        count = 0
        number_line_infile = 1
        for line in file:
            if number_line_infile in test_data:
                pos_end = line.find("] ")
                sentence = line[pos_end + 2:]
                sentence = sentence + '\n'
                file_w.write(sentence)
                count = count + 1
            number_line_infile = number_line_infile + 1
    file.close()
file_w.close()
print('Seleccionados aleatoriamente ', count, 'abstracts')'''

nlp = spacy.load("en_core_web_trf")
with open(f"{WORD.upper()}_clean_test_data.txt", "w", encoding="utf8") as file_w:
    with open(f"{WORD.upper()}_test_data.txt", encoding="utf8") as file:
        lines = file.readlines()
        for line in lines:
            text = line.strip()
            if len(text) < 4:
                continue
            doc = nlp(text)
            print('=', end='')
            for sent in doc.sents:
                if ' where ' in sent.text:
                    file_w.write(sent.text + '\n')
    file.close()
file_w.close()











