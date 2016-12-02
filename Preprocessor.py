# -*- coding: utf-8 -*-
"""
Created on Thu Dec  1 11:08:32 2016

@author: ZHULI
"""
import re, sys
from nltk.stem import PorterStemmer
from read_npl_tag import get_nlp_annotate, get_all_nlp_tag

class Preprocessor():
    def __init__(self, isReversed = False, isStop = False, isStem = False):
        self.isReversed = isReversed
        self._isStem = isStem
        self._stops = set()
        if isStop:
            self.readStopList()
        
    def readStopList(self, file = 'stop_list.txt'):
        f = open(file,'r')
        for line in f:
            self._stops.add(line.strip())

    def getLine(self, line):
        res = ''
        for token in self.getToken(line):
            res = res + ' ' + token
        return res

    def getToken(self, line):
        regex_word = re.compile('\w+')
        words = regex_word.findall(line)
        if self.isReversed:
            words.reverse()
        for token in words:
            if token not in self._stops:
                if self._isStem:
                    yield PorterStemmer().stem(token)
                else:
                    yield token

    def getWord(self, word):
        if word not in self._stops:
            if self._isStem:
                return PorterStemmer().stem(word)
            else:
                return word
        else:
            return None
    
class Preprocessor_WP(Preprocessor):
    def __init__(self, isSimplePOS, isReversed = False, isStop = False, isStem = False):
        Preprocessor.__init__(self, isReversed = isReversed, isStop = isStop, isStem = isStem)
    
    def getToken_wordpos(self, line):
        wordpos_pairs = get_all_nlp_tag(line, True)
        if self.isReversed:
            wordpos_pairs.reverse()
        for wordpos in wordpos_pairs:
            word, pos = wordpos
            yield self.getWord(word.lower()), pos

    # get a list of pos tags of the words in the line
    def getPOS_line(self, line):
        return get_all_nlp_tag(line)
        
    def getSimplePOS(self, POS):
        pass