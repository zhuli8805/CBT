# -*- coding: utf-8 -*-
"""
Created on Wed Nov 30 23:46:54 2016

@author: Yixuan Li
"""

"""
java -mx4g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer
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

pattern = 'cbtest_*'
#pattern = 'test*'
if len(sys.argv) > 1:
    pattern = sys.argv[1]
data_path = 'CBTest Datasets\CBTest\data'

file_in_list = glob(join(data_path, pattern))
file_out_list = []
for f_in in file_in_list:
    base = basename(f_in)
    f_out = join(data_path, splitext(base)[0]+'_WP'+splitext(base)[1])
    file_out_list.append(f_out)
    

def display_files():
    for f_in, f_out in zip(file_in_list, file_out_list):
        print(basename(f_in))
        print(basename(f_out))


def glob_CBT_files():
    for f_in, f_out in zip(file_in_list, file_out_list):
        with open(f_in, 'r') as file_in:
            with open(f_out, 'w') as file_out:
                print('Start processing ' + basename(f_in))
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
    answer_pair = []
    candidates_pair = []
    output_list = [str(num)]
    if num == 21:
        content_pair, missing_word_idx = identify_query_tag(content)
        candidates_pair_dict = identify_target_tag(content, text_list, candidates, missing_word_idx)
        candidates_pair.append('|'.join([':'.join([x,y]) for x, y in candidates_pair_dict.items()]))
        answer_pair.append(':'.join([answer,candidates_pair_dict[answer]]))
        output_list += content_pair + answer_pair + candidates_pair
    else:
        output_list.append(identify_tag(content))
    return output_list

def identify_tag(content):
    content_pair = []
    output = corenlp.annotate(content, properties=corenlp_settings)
    for line in output.splitlines():
        m = re_nlp_annotate.match(line)
        if m:
            if re_punct.match(m.group(1)):
                continue
            content_pair.append(':'.join([m.group(1), m.group(2)]))
    content_tag = ' '.join(content_pair)
    return content_tag
    
def identify_query_tag(content):
    content_pair = []
    output = corenlp.annotate(content, properties=corenlp_settings)
    num = 0
    missing_word_idx = None
    for line in output.splitlines():
        num += 1
        m = re_nlp_annotate.match(line)
        if m:
            if re_punct.match(m.group(1)):
                continue
            if m.group(1) == missing_word:
                missing_word_idx = num - 1
            content_pair.append(':'.join([m.group(1), m.group(2)]))
    content_tag = [' '.join(content_pair)]
    return content_tag, missing_word_idx

def identify_target_tag(content, splitted_content, candidates, missing_word_idx):
    target_tag = {}
    #missing_word_idx = identify_missing_word_pos(splitted_content) + 2
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
    display_files()
    glob_CBT_files()


if __name__ == '__main__':
    main()

