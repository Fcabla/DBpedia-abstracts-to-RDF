import os

FOLDER_PATH = 'log_files/'

if not os.path.isdir(FOLDER_PATH):
    os.mkdir(FOLDER_PATH)


def tracking_log(input, level):
    with open(f'{FOLDER_PATH}tracking.txt', 'a', encoding='utf8') as f:
        if level == 0:
            f.write(f'ORIGINAL SENTENCE: {input}' + '\n')
        if level == 1:
            f.write(f'  COREFEREE: {input.text}' + '\n')
        if level == 2:
            f.write('  LIST OF SENTENCES:\n')
            for i, sent in enumerate(input):
                f.write(f'    {i}: {sent}\n')
        if level == 3:
            f.write('  SIMPLE SENTENCES:\n')
            for i, sent in enumerate(input):
                f.write(f'    {i}: {sent}\n')
        if level == 4:
            f.write('  TEXT TRIPLES:\n')
            for i, sent in enumerate(input):
                f.write(f'    {i}: {sent.__repr__()}\n')
        if level == 5:
            f.write('  RDF TRIPLES:\n')
            for i, sent in enumerate(input):
                f.write(f'    {i}: {sent}\n')
    f.close()


def triple_with_no_uri_log(triple, item):
    with open(f'{FOLDER_PATH}literals_log.txt', 'a', encoding='utf-8') as f:
        f.write(f'>>SENTENCE: {triple.sent}\n')
        f.write(f'{triple.subj} | {triple.pred} | {triple.objct}\n')
        f.write(f'Literal: <{item}>\n')
    f.close()


def triple_with_no_uri_log_subject(triple, item):
    with open(f'{FOLDER_PATH}literals_log.txt', 'a', encoding='utf-8') as f:
        f.write(f'>>SENTENCE: {triple.sent}\n')
        f.write(f'{triple.subj} | {triple.pred} | {triple.objct}\n')
        f.write(f'Subject not FOUND: <{item}>\n')
    f.close()


def triple_with_no_uri_log_object(triple, item):
    with open(f'{FOLDER_PATH}literals_log.txt', 'a', encoding='utf-8') as f:
        f.write(f'>>SENTENCE: {triple.sent}\n')
        f.write(f'{triple.subj} | {triple.pred} | {triple.objct}\n')
        f.write(f'Literal object <to be>: <{item}>\n')
    f.close()

def triple_with_no_uri_log_object2(triple, item):
    with open(f'{FOLDER_PATH}literals_log.txt', 'a', encoding='utf-8') as f:
        f.write(f'>>SENTENCE: {triple.sent}\n')
        f.write(f'{triple.subj} | {triple.pred} | {triple.objct}\n')
        f.write(f'Literal object: <{item}>\n')
    f.close()
