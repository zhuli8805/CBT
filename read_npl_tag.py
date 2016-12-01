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

def get_all_nlp_tag(text, paired_output=False, nlp=nlp):
    output = nlp.annotate(text, properties=nlp_settings)
    re_annotate_tag = re.compile('\[Text=(\S+).*PartOfSpeech=(\S+)')
    pos_list = []
    re_symbols = re.compile('^[^a-zA-Z]+$')
    for line in output.splitlines():
        m = re_annotate_tag.match(line)
        if m:
            if re_symbols.match(m.group(1)):
                continue
            if paired_output:
                pos_list.append([m.group(1), m.group(2)])
            else:
                pos_list.append(m.group(2))
    return(pos_list)

def get_nlp_annotate(text, candidates=None, nlp=nlp):
    output = nlp.annotate(text, properties=nlp_settings)
    re_annotate_tag = re.compile('\[Text=(\S+).*PartOfSpeech=(\S+)')
    pos_arround_missing_word = identify_annotate_tag(output, re_annotate_tag, missing_word)
    if candidates:
        pos_of_target = identify_target_tag(text, candidates, re_annotate_tag, nlp)
        return(pos_arround_missing_word, pos_of_target)
    else:
        return(pos_arround_missing_word)
    
def identify_annotate_tag(nlp_output, regex, target):
    pos_list_full = []
    pos_list = []
    target_index = 0
    re_symbols = re.compile('^[^a-zA-Z]+$')
    for line in nlp_output.splitlines():
        m = regex.match(line)
        if m:
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
    
def identify_target_tag(text, candidates, regex, nlp=nlp):
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
            
def demo():
    # Get the POS info arround XXXXX and of candidates.
    a, b = get_nlp_annotate(text=text, candidates=candidates, nlp=nlp)
    print(list(zip(candidates,b)))
    # Get the POS info for a sentence.
    a = get_all_nlp_tag(text, nlp=nlp, paired_output=True)
    print(a)

def getToken_wordpos(line):
    wordpos_pairs = get_all_nlp_tag(line, True)
    for wordpos in wordpos_pairs:
        word, pos = wordpos
        yield word, pos
            
if __name__ == '__main__':
#    demo()
    a, b = get_nlp_annotate(text, candidates)
    print(dict(zip(candidates,b)))
    print('a===', a)
    print('b===', b)
    c = get_nlp_annotate(text)
    print('c===', c)
    d = get_all_nlp_tag('this is a fucking apple')
    print('d===', d)
    e = get_all_nlp_tag('this is a fucking apple', True)
    print('e===', e)
    e.reverse()
    print('f===', e)
    pairs = []
    for pair in getToken_wordpos('this is a fucking apple'):
        pairs = pairs + [pair]
    print ('g===', pairs)
    pair_START = [['START', 'START']]
    pair_END = [['END', 'END']]
    pairs = pair_START + pair_START + pairs + pair_END + pair_END
    print('123', pairs)
    for pair in pairs:
        word, pos = pair
        print ('h===',word,'-----',pos)
