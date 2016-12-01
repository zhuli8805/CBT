# -*- coding: utf-8 -*-
"""
Created on Wed Nov 30 23:46:54 2016

@author: Yixuan Li
"""

import re, sys
from pycorenlp import StanfordCoreNLP
from os.path import basename, join, splitext
from glob import glob

missing_word = 'XXXXX'
corenlp = StanfordCoreNLP('http://localhost:9000')
corenlp_settings = {'annotators': 'tokenize,ssplit,pos,ner', "outputFormat": "text"}
re_nlp_annotate = re.compile('\[Text=(\S+).*PartOfSpeech=(\S+)')
re_punct = re.compile('^[^a-zA-Z]+$')

pattern = 'cbtest_CN*'
if len(sys.argv) > 1:
    pattern = sys.argv[1]
    
data_path = 'D:\Yixuan Li\Documents\TUoS\Industrial Team Project\CBTest\CBTest\data'
file_in_list = glob(join(data_path, pattern))
file_out_list = []
for f_in in file_in_list:
    base = basename(f_in)
    f_out = join(data_path, splitext(base)[0]+'_WP'+splitext(base)[1])
    file_out_list.append(f_out)
    

def demo():
    for f_in, f_out in zip(file_in_list, file_out_list):
        print(f_in+'\n'+f_out)


def glob_CBT_files():
    for f_in, f_out in zip(file_in_list, file_out_list):
        with open(f_in, 'r') as file_in:
            with open(f_out, 'w') as file_out:
                print('Start processing ' + f_in)
                read_and_write(file_in, file_out)


def read_and_write(file_in, file_out):
    for line in file_in:
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
    #glob_CBT_files()
    pass

if __name__ == '__main__':
    main()
