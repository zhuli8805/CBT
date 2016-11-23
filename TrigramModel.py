# -*- coding: utf-8 -*-
"""
Created on Tue Nov 22 14:39:42 2016

@author: ZHULI
"""

import re
from read_data import ReadData
from nltk.stem import PorterStemmer

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
    
    def getToken(self, line):
        regex_word = re.compile('[a-z]+')
        words = regex_word.findall(line.lower())
        if self.isReversed:
            words.reverse()
        
        for token in words:
            if token not in self._stops:
                if self._isStem:
                    yield PorterStemmer().stem(token)
                else:
                    yield token

class Three():
    def __init__(self):
        self.__times = 0 # time of appearance given previous two words
        self.__p = 0 
    
    def compute(self, levelsize):
        self.__p = self.__times/levelsize
    
    def set_times(self, times):
        self.__times = times
        
    def get_times(self):
        return self.__times
        
    def get_p(self):
        return self.__p
        
    def add(self):
        self.__times += 1

class WordDict(dict):
    def __init__(self, levelNum, default = None):
        dict.__init__(self)
        self.default = default
        # time of appearance given previous one word, 
        # does not equal to len(self) as the word is not necessarily have a following word
        # ie. bigram != trigram
        self.__times = 0 # should be zero for the first word
        self.__p = 0 # should be zero for the first word
        # 1: this word is first word, first word has sublevel of WordDict()
        # 2: this word is second word, second word has sublevel of Three()
        self.__levelNum = levelNum
        
    def compute(self, levelTimes):
        if levelTimes:
            self.__p = self.__times / levelTimes
        subLevelTimes = 0
        for word in self:
            subLevelTimes += self[word].get_times()
        for word in self:            
            self[word].compute(subLevelTimes)
        
    def add(self):
        self.__times += 1
    
    def load(self, times, part):
        self.__times = times
        if self.__levelNum is 1:
            regex_twothreeid_pair = re.compile('[\w:\d]*\[[\w:\d|]*\]') # eat:1[apple:1|orange:1]
            regex_two_threeids = re.compile('([\w:\d]*)\[([\w:\d|]*)\]') # eat:1 and [apple:1|orange:1]
            for pair_twothreeid in regex_twothreeid_pair.findall(part):
                two_counts, threeids = regex_two_threeids.search(pair_twothreeid).groups() 
                two, twoCounts = two_counts.split(':')
                if two not in self:
                    self[two] = WordDict(2) 
                self[two].load(int(twoCounts), threeids)
        if self.__levelNum is 2:
            for three_counts in part.split('|'): # apple:1|orange:1
                if len(three_counts.split(':')) is 2:
                    three, threeCounts = three_counts.split(':') # apple:1
                    if three not in self:
                        self[three] = Three()
                    self[three].set_times(int(times))
    
    # get bigram value [ NOT recommanded ]
    def get_p(self,):
        if self.__levelNum is not 1:
            return self.__p
        else:
            print('>>> NO P VALUE FOR THE FIRST WORD! <<<')
            return None
            
    def get_times(self):
        return self.__times

class TrigramModel(dict):
    def __init__(self, default = None, isReversed = False, isStop = False, isStem = False):
        dict.__init__(self)
        self.default = default  
        self.isReversed = isReversed
        self.isStop = isStop
        self.isStem = isStem
        self.__pre = Preprocessor(isReversed = self.isReversed, isStop = self.isStop, isStem = self.isStem)
    
    # generate filename according to the configurations
    def _getFileName(self, initName):
        filename = initName        
        if self.isReversed:
            filename += '_reverse'    
        if self.isStop:
            filename += '_stop'
        if self.isStem:
            filename += '_stem'
        filename += '.txt'
        return filename
       
    # get probability value for bigram or trigram [ RECOMMANDED ]
    def get_p(self, one, two, three = None):
        if one not in self:
            return 0
        if two not in self[one]:
            return 0
        if three:
            if three not in self[one][two]:
                return 0
            return self[one][two][three].get_p() # trigram
        else:
            return self[one][two].get_p() # bigram
        
    def update_file(self, filename):
        print('<update_file....>:\n%s' % filename)
        data = ReadData(filename, True, None)
        for line in data:
            one = None
            two = None
            for word in self.__pre.getToken(line):
                if two:
                    if two not in self:
                        self[two] = WordDict(1)
                    self[two][word] = WordDict(2)
                    self[two][word].add()
                if one:
                    if word not in self[one][two]:
                        self[one][two][word] = Three()
                    self[one][two][word].add()
                one = two
                two = word
                
    def store(self):
        filename = self._getFileName('Trigram')
        print('<storing...> : \n%s' % filename)
        try:
            indexfile = open(filename,'w')
        except IOError:
            print('FAILURE: INDEX file loading failed!')
            return False
        else:
            # write trigram
            for one in self.keys():
                print(one, end = '', file = indexfile)
                print('{', end = '', file = indexfile)
                for two in self[one].keys():
                    print('%s:%d' % (two, self[one][two].get_times())
                        , end = '', file = indexfile)
                    print('[', end = '', file = indexfile)
                    is1st3 = True
                    for three in self[one][two].keys():
                        if not is1st3:
                            print('|', end = '', file = indexfile)
                        else:
                            is1st3 = False
                        print('%s:%d' % (three, self[one][two][three].get_times())
                            , end = '', file = indexfile)
                    print(']', end = '', file = indexfile)
                print('}', file = indexfile)
        indexfile.close()
        print('<< stored >>')

    def compute(self):
        print('<computing...>')
        for one in self:
            self[one].compute(None)
    
    def load(self):
        filename = self._getFileName('Trigram')
        print('<loading...> : \n%s' % filename)
        try:
            indexfile = open(filename,'r')
        except IOError:
            print('FAILURE: INDEX file loading failed!')
            return False
        else:
            regex_one_twothree = re.compile('^([\w]+){(.+)}') # word{....}
            for line in indexfile:
#                print('line = ', line)
                one, twothree = regex_one_twothree.search(line).groups() # word{....}
                if one not in self:
                    self[one] = WordDict(1)
                self[one].load(0, twothree)
        indexfile.close()
        print('<loaded>')
        self.compute()


trainingFileName1 = '..\..\..\..\CBTest Datasets\CBTest\data\cbt_train.txt'
trainingFileName2 = '..\..\..\..\CBTest Datasets\CBTest\data\cbtest_CN_train.txt'
trainingFileName3 = '..\..\..\..\CBTest Datasets\CBTest\data\cbtest_NE_train.txt'
trainingFileName4 = '..\..\..\..\CBTest Datasets\CBTest\data\cbtest_P_train.txt'
trainingFileName5 = '..\..\..\..\CBTest Datasets\CBTest\data\cbtest_V_train.txt'

test = TrigramModel(isStop = True, isStem = True, isReversed = False)
test.update_file(trainingFileName1)
test.compute()
test.store()
print(test.get_p('pu','pu')) # recommanded way for bigram p
print(test.get_p('pu','pum')) # recommanded way for trigram p 
print(test['pu']['pu'].get_times()) 
print(test['pu']['pu'].get_p())
test.update_file(trainingFileName2)
test.update_file(trainingFileName3)
test.update_file(trainingFileName4)
test.update_file(trainingFileName5)

#print('<<done!>>')

### loading result test
#test2 = TrigramModel(isStop = True, isStem = True, isReversed = True)
##test2.load_idword()
#test2.load()
#### mattock{blow:1[farther:1]mountain:1[search:1]}
#print(test2['mattock']['blow'].get_times()) 
#print(test2['mattock']['blow'].get_p())
#### pu{pu:1[pu:1|pum:1]pum:1[poh:1]}
#print(test2['pu']['pu'].get_times())
#print(test2['pu']['pu'].get_p())
#print(test2['pu']['pu']['pum'].get_times())
#print(test2['pu']['pu']['pum'].get_p())
#print(test2['pu']['pum']['poh'].get_p())
##print(test2['pu']['pu']['poh'].get_p()) # not existed
#print(test2.get_p('pu','pu')) # recommanded way for bigram p
#print(test2.get_p('pu','pum')) # recommanded way for trigram p 