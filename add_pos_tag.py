# -*- coding: utf-8 -*-
"""
Created on Wed Nov 30 23:46:54 2016

@author: Yixuan Li
"""

import re
from pycorenlp import StanfordCoreNLP

missing_word = 'XXXXX'
corenlp = StanfordCoreNLP('http://localhost:9000')
corenlp_settings = {'annotators': 'tokenize,ssplit,pos,ner', "outputFormat": "text"}
re_nlp_annotate = re.compile('\[Text=(\S+).*PartOfSpeech=(\S+)')
re_punct = re.compile('^[^a-zA-Z]+$')

file_1 = 'cbtest_CN_test_2500ex.txt'
file_2 = 'test_new.txt'

def glob_CBT_files():
    with open(file_1, 'r') as file_in:
        with open(file_2, 'w') as file_out:
            read_and_write(file_in, file_out)

def read_and_write(file_in, file_out):
    num = 0
    for line in file_in:
        num += 1
        if num == 2244:
            return 0 
        if line.split():
            output_list = get_nlp_tag(line)
            file_out.write('\t'.join(output_list))
        file_out.write('\n')

def get_nlp_tag(text):
    text_list = text.split()
    num = int(text_list.pop(0))
    if num == 21:
        candidates = text_list.pop().split('|')
        answer = text_list.pop()
    content = ' '.join(text_list)
    output = corenlp.annotate(content, properties=corenlp_settings)
    content_pair = []
    answer_pair = []
    candidates_pair = []
    candidates_pair_dict = {}
    output_list = [str(num)]
    for line in output.splitlines():
        m = re_nlp_annotate.match(line)
        if m:
            if re_punct.match(m.group(1)):
                continue
            content_pair.append(':'.join([m.group(1), m.group(2)]))
    output_list.append(' '.join(content_pair))
    if num == 21:
        candidates_pair_dict = identify_target_tag(content, text_list, candidates)
        candidates_pair.append('|'.join([':'.join([x,y]) for x, y in candidates_pair_dict.items()]))
        answer_pair.append(':'.join([answer,candidates_pair_dict[answer]]))
        output_list += answer_pair + candidates_pair
    return output_list

def identify_target_tag(content, splitted_content, candidates):
    target_tag = {}
    missing_word_idx = identify_missing_word_pos(splitted_content) + 2
    for word in candidates:
        output = corenlp.annotate(content.replace(missing_word, word), 
                                  properties=corenlp_settings)
        line = output.splitlines()[missing_word_idx]
        m = re_nlp_annotate.match(line)
        if m:
            target_tag[m.group(1)] = m.group(2)
    return target_tag

    
def identify_missing_word_pos(splitted_content):
    for i in range(len(splitted_content)-1):
        if splitted_content[i] == missing_word:
            return i

def main():
    glob_CBT_files()

if __name__ == '__main__':
    main()
