# -*- coding: utf-8 -*-
"""
Created on Tue Nov 29 15:35:24 2016

@author: Yixuan Li
"""

# java -mx4g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer -annotators tokenize,ssplit,pos,ner

import re
from pycorenlp import StanfordCoreNLP

nlp = StanfordCoreNLP('http://localhost:9000')
text = 'Then the runner awoke , jumped up , and saw that his pitcher was empty and the King \'s XXXXX far ahead . \n'
candidates = ('daughter', 'husband', 'man', 'manners', 'past', 'skull', 'sky', 'spectator', 'stream', 'town')
missing_word = 'XXXXX'
nlp_settings = {'annotators': 'tokenize,ssplit,pos,ner', "outputFormat": "text"}


def get_nlp_annotate(nlp, text, candidates=None, ne=True):
    output = nlp.annotate(text, properties=nlp_settings)
    re_annotate_tag = re.compile('\[Text=(\w+).*PartOfSpeech=(\w+).*NamedEntityTag=(\w+)')
    #print(identify_annotate_tag(output, re_annotate_tag, missing_word))
    print(identify_target_tag(nlp, text, candidates, re_annotate_tag))
    
def identify_annotate_tag(nlp_output, regex, target):
    pos_list_full = []
    pos_list = []
    target_index = 0
    re_symbols = re.compile('^[^a-zA-Z]+$')
    for line in nlp_output.splitlines():
        m = regex.match(line)
        if m:
            print(m.groups())
            if re_symbols.match(m.group(1)):
                continue
            if m.group(1) == target:
                target_index = len(pos_list_full)                
            pos_list_full.append(m.group(2))

    for i in range(target_index - 2, target_index + 3):
        if i < 0 or i >= len(pos_list_full):
            pos_list.append(None)
        elif i != target_index:
            pos_list.append(pos_list_full[i])
    return pos_list

def identify_target_tag(nlp, text, candidates, regex):
    pos_list = []
    missing_word_idx = identify_missing_word_pos(text) + 2
    for word in candidates:
        output = nlp.annotate(text.replace(missing_word, word), properties=nlp_settings)
        line = output.splitlines()[missing_word_idx]
        m = regex.match(line)
        if m:
            if m.group(1) == word:
                pos_list.append(m.group(2))
    return pos_list
    
def identify_missing_word_pos(text):
    splitted_text = text.split(' ')
    for i in range(len(splitted_text)-1):
        if splitted_text[i] == missing_word:
            return i
    
    
if __name__ == '__main__':
    get_nlp_annotate(nlp, text, candidates)
