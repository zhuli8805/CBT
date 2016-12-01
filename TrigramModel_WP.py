# -*- coding: utf-8 -*-
"""
Created on Tue Nov 22 14:39:42 2016

@author: ZHULI
"""

import re, time, sys
from read_data import ReadData
from TrigramModel import Three, WordDict, TrigramModel
from Preprocessor import Preprocessor_WP

class Three_WP(Three):
    def __init__(self):
        Three.__init__(self)
        # times of POS of this word if self is a word
        # times of word of this POS if self is a POS
        self.__myAlterTimesDict = {}
        
    # add alter times
    def add_myAlter(self, alter, times = 1):
        if alter not in self.__myAlterTimesDict.keys():
            self.__myAlterTimesDict[alter] = times
        else:
            self.__myAlterTimesDict[alter] += times
    
    def set_myAlterTimes(self, alter, times):    
        self.__myAlterTimesDict[alter] = int(times)
    
    # get alter and times
    def get_myAlterTimes(self):
        for alter in self.__myAlterTimesDict.keys():
            yield alter, self.__myAlterTimesDict[alter]

class WordDict_WP(WordDict):
    def __init__(self, levelNum, isPOS, default = None):
        WordDict.__init__(self, levelNum = levelNum, default = default)
        # recognize self as a dict of POS or a dict of word
        # updates, filename will be done in different ways
        self.__isPOS = isPOS
        # times of POS of this word if self is a word
        # times of word of this POS if self is a POS
        self.__myAlterTimesDict = {}
        # __alterDict (POS/word:Probability) is generated in compute()
        # for the use of guessing POS/word based on given word/POS nearby
        self.__nextAlterpDict = {} # POS/word of next word
        
    def compute(self, levelTimes):
        # compute for simple WordDict
        WordDict.compute(self, levelTimes)
        # compute for alter information
        self.__nextAlterpDict = {}
        subAlterTimes = 0
        for word in self:
            if word not in ['START', 'END']:
                for alter, times in self[word].get_myAlterTimes():
                    print(alter, times)
                    print('subAlterTimes',subAlterTimes)
                    subAlterTimes += times
                    if alter not in self.__nextAlterpDict.keys():
                        self.__nextAlterpDict[alter] = times
                    else:
                        self.__nextAlterpDict[alter] += times
        for alter in self.__nextAlterpDict.keys():
            if alter not in ['START', 'END']:
                self.__nextAlterpDict[alter] = self.__nextAlterpDict[alter] / subAlterTimes
    
    # load word/POS mixed model  
    def load(self, times, part):
        self.__times = times
        if self.__levelNum is 1:
            # eat:1<NN:1|VB:1>[apple:1<NN:1|VB:1>|orange:1<NN:1|VB:1>]
            regex_twothreeid_pair = re.compile('[\w:\d]*<[\w:\d|]*>\[[<>\w:\d|]*\]') 
            # eat:1<NN:1|VB:1> and [apple:1<NN:1|VB:1>|orange:1<NN:1|VB:1>]
            regex_twoalter_threeids = re.compile('([\w:\d]*<[\w:\d|]*>)\[([<>\w:\d|]*)\]')
            # eat:1 and NN:1|VB:1
            regex_two_alter = re.compile('([\w:\d]*)<([\w:\d|]*)>')
            for pair_twothreeid in regex_twothreeid_pair.findall(part):                
                two_alter, threeids = regex_twoalter_threeids.search(pair_twothreeid).groups() 
                two_counts, alters = regex_two_alter.search(two_alter).groups()
                two, twoCounts = two_counts.split(':')
                if two not in self:
                    self[two] = WordDict(2, isStanford = True, isPOS = self.__isPOS)
                self[two].load(int(twoCounts), threeids)
                for alter_counts in alters.split('|'):
                    alter, counts = alter_counts.split(':')
                    self[two].set_myAlterTimes(alter, counts)
        if self.__levelNum is 2:
            # part is: [apple:1<NN:1|VB:1>|orange:1<NN:1|VB:1>]
            regex_threealter_pair = re.compile('[\w:\d]*<[\w:\d|]*>')
            regex_threecounts_alters = re.compile('([\w:\d]*)<([\w:\d|]*)>')
            # apple:1<NN:1|VB:1>
            for threealters in regex_threealter_pair.findall(part): 
                # apple:1 and NN:1|VB:1
                three_counts, alters = regex_threecounts_alters.search(threealters).groups() 
                three, threeCounts = three_counts.split(':') # apple:1
                if three not in self:
                    self[three] = Three()
                self[three].set_times(int(times))
                # NN:1|VB:1
                for altercounts in alters.split('|'):
                    alter, counts = altercounts.split(':')
                    self[three].set_myAlterTimes(alter, counts)
    
    # get alter and times
    def get_myAlterTimes(self):
        for alter in self.__myAlterTimesDict.keys():
            yield alter, self.__myAlterTimesDict[alter]
    
    # add alter times
    def add_myAlter(self, alter):
        if alter not in self.__myAlterTimesDict.keys():
            self.__myAlterTimesDict[alter] = 1
        else:
            self.__myAlterTimesDict[alter] += 1
            
    # get probability of next POS/word
    def get_alterp(self, alter):
        if alter in self.__nextAlterpDict.keys():
            return self.__nextAlterpDict[alter]
        else:
            return 0
    
    def set_myAlterTimes(self, alter, times):    
        self.__myAlterTimesDict[alter] = int(times)
        
class TrigramModel_WP(TrigramModel):
    def __init__(self, isPOS, isReversed = False, isStop = False, isStem = False, default = None):
        TrigramModel.__init__(self, isReversed = isReversed, isStop = isStop, isStem = isStem, default = default)
        self.__pre = Preprocessor_WP(isReversed = self.isReversed, isStop = self.isStop, isStem = self.isStem)
        # recognize self as a dict of POS or a dict of word
        # updates, filename will be done in different ways
        self.__isPOS = isPOS
        
    # generate filename according to the configurations
    def _getFileName(self, initName):
        filename = initName + '_WP'
        if self.__isPOS:
            filename += '_POS'            
        return TrigramModel._getFileName(self, filename)
            
    # get probability value for bigram or trigram [ RECOMMANDED ]
    def get_alterp(self, one, two, three = None):
        if one is None or two is None:
            return 0
        if one not in self:
            return 0        
        if three: # three should be POS
            if two not in self[one]:
                return 0
            return self[one][two].get_alterp(three) # trigram
        else: # two should be POS
            return self[one].get_alterp(two) # bigram
    
    # update the data of line if this is a word dict
    def update_line_word(self, line):
        one = None
        two = None
        pair_START = [['START', 'START']]
        pair_END = [['END', 'END']]
        pairs = []
        for pair in self.__pre.getToken_wordpos(line):
            pairs = pairs + [pair]
        pairs = pair_START + pair_START + pairs + pair_END + pair_END
#        print ('update_line_word pairs = ', pairs)
        for pair in pairs:
#            print('pair = ', pair)
            word, pos = pair
            if two:
                if two not in self:
                    self[two] = WordDict(1, isPOS = self.__isPOS)
                self[two][word] = WordDict(2, isPOS = self.__isPOS)
                self[two][word].add()
                self[two][word].add_myAlter(pos)
            if one:
                if word not in self[one][two]:
                    self[one][two][word] = Three()
                self[one][two][word].add()
                self[one][two][word].add_myAlter(pos)
            one = two
            two = word
            
    # update the data of line if this is a POS dict
    def update_line_POS(self, line):
        one = None
        two = None
        pair_START = [['START', 'START']]
        pair_END = [['END', 'END']]
        pairs = []
        for pair in self.__pre.getToken_wordpos(line):
            pairs = pairs + [pair]
        pairs = pair_START + pair_START + pairs + pair_END + pair_END
        for pair in pairs:
            word, pos = pair
            if two:
                if two not in self:
                    self[two] = WordDict(1, isPOS = self.__isPOS)
                self[two][pos] = WordDict(2, isPOS = self.__isPOS)
                self[two][pos].add()
                self[two][pos].add_myAlter(word)
            if one:
                if word not in self[one][two]:
                    self[one][two][pos] = Three()
                self[one][two][pos].add()
                self[one][two][pos].add_myAlter(word)
            one = two
            two = pos
        
    def update_line(self, line):
        if self.__isPOS:
            self.update_line_POS(line)
        else:
            self.update_line_word(line)
            
    def store(self, initFileName = '.\\Trigram Data\\Trigram'):
        filename = self._getFileName(initFileName)
        print('<storing WP...> : \n%s' % filename)
        try:
            indexfile = open(filename,'w')
        except IOError:
            print('FAILURE: INDEX file loading failed!')
            return False
        else:
            # write trigram
            for one in self.keys():
                # print first word
                print(one, end = '', file = indexfile)
                # print second word
                print('{', end = '', file = indexfile)
                for two in self[one].keys():
                    print('%s:%d' % (two, self[one][two].get_times())
                        , end = '', file = indexfile)
                    # print second word's alter
                    print('<', end = '', file = indexfile)
                    is1stTwoAlter = True
                    for two_alter, two_alterTimes in self[one][two].get_myAlterTimes():
                        if is1stTwoAlter:
                            is1stTwoAlter = False
                        else:
                            print('|', end = '', file = indexfile)
                        print('%s:%d' % (two_alter, two_alterTimes), end = '', file = indexfile)
                    print('>', end = '', file = indexfile)
                    # print third word    
                    print('[', end = '', file = indexfile)
                    is1st3 = True
                    for three in self[one][two].keys():
                        if not is1st3:
                            print('|', end = '', file = indexfile)
                        else:
                            is1st3 = False
                        print('%s:%d' % (three, self[one][two][three].get_times())
                            , end = '', file = indexfile)  
                        # print third word's alter
                        print('<', end = '', file = indexfile)
                        is1stThreeAlter = True
                        for three_alter, three_alterTimes in self[one][two][three].get_myAlterTimes():
                            if is1stThreeAlter:
                                is1stThreeAlter = False
                            else:
                                print('|', end = '', file = indexfile)
                            print('%s:%d' % (three_alter, three_alterTimes), end = '', file = indexfile)
                        print('>', end = '', file = indexfile)
                    print(']', end = '', file = indexfile)
                print('}', file = indexfile)
        indexfile.close()
        print('<< stored >>')
    
    def load(self, initFileName = '.\\Trigram Data\\Trigram'):
        filename = self._getFileName(initFileName)
        print('<loading WP...> : \n%s' % filename)
        try:
            indexfile = open(filename,'r')
        except IOError:
            print('FAILURE: INDEX file loading failed!')
            return False
        else:
            regex_one_twothree = re.compile('^([\w]+){(.+)}') # word{....}
            for line in indexfile:
#                print('line = ', line)
                one, twothree = regex_one_twothree.search(line).groups() # word and {....}
                if one not in self:
                    self[one] = WordDict(1, isPOS = self.__isPOS)
                self[one].load(0, twothree)
        indexfile.close()
        self.compute()
        print('<loaded>')

def Run_BuildData_WP(isPOS, isStop, isStem, isReversed):
    trainingFiles = [
#                     '..\..\..\..\CBTest Datasets\CBTest\data\cbt_test.txt',
#                     '..\..\..\..\CBTest Datasets\CBTest\data\cbt_train.txt',
#                     '..\..\..\..\CBTest Datasets\CBTest\data\cbt_valid.txt',
                     '..\..\..\..\CBTest Datasets\CBTest\data\cbtest_CN_train.txt',
                     '..\..\..\..\CBTest Datasets\CBTest\data\cbtest_NE_train.txt',
                     '..\..\..\..\CBTest Datasets\CBTest\data\cbtest_P_train.txt',
                     '..\..\..\..\CBTest Datasets\CBTest\data\cbtest_V_train.txt'
                    ]        
    myTrigram = TrigramModel(isPOS = isPOS, isStop = isStop, isStem = isStem, isReversed = isReversed)
    for file in trainingFiles:
        print('Building Data', isPOS, isStop, isStem, isReversed)
        myTrigram.update_file(file)
    myTrigram.compute()
    myTrigram.store()
    print('<<done!>>')

##### write and read test for [WP] Trigram
def Run_testWR_WP():
    myTrigram = TrigramModel(isPOS = False, isStop = False, isStem = False, isReversed = False)
    myTrigram.update_file('test.txt')
    myTrigram.compute()
    myTrigram.store()
    myTrigram2 = TrigramModel(isPOS = False, isStop = False, isStem = False, isReversed = False)
    myTrigram2.load()
    myTrigram2.store()

#print('======')
#print(myTrigram.get_alterp('this','VBZ'))
#print(myTrigram['this'].get_alterp('VBZ'))
#for pos,times in myTrigram['this']['is'].get_myAlterTimes():
#    print(pos, times)
#print(myTrigram['this']['is'].get_alterp('DT'))
    
#filename = '..\..\..\..\CBTest Datasets\CBTest\data\cbtest_P_train.txt'    
#import linecache
#stre = linecache.getlines(filename)
#count = linecache.getline(filename,123)
#print (count)
    
    
     # Data test
#    print(test.get_p('our', 'family')) # recommanded way for bigram p
#    print(test.get_p('my', 'dear')) # recommanded way for trigram p 
#    print(test['our']['family'].get_times())

### loading result test
#test2 = TrigramModel(isStop = False, isStem = False, isReversed = False)
#test2.load()
#print(test2.get_p('our', 'family')) # recommanded way for bigram p
#print(test2.get_p('my', 'dear')) # recommanded way for trigram p 
#print(test2['our']['family'].get_times())