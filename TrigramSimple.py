# -*- coding: utf-8 -*-
"""
Created on Tue Nov 22 14:39:42 2016

@author: ZHULI
"""

import re, time
from read_data import ReadData
from Preprocessor import Preprocessor
from os.path import basename

class Three():
    def __init__(self):
        self._times = 0 # time of appearance given previous two words
        self.__p = 0 
    
    def compute(self, levelsize):
        self.__p = self._times/levelsize
    
    def set_times(self, times):
        self._times = times
        
    def get_times(self):
        return self._times
        
    def get_p(self):
        return self.__p
        
    def add(self):
        self._times += 1

class WordDict(dict):
    def __init__(self, levelNum, default = None):
        dict.__init__(self)
        self.default = default
        # time of appearance given previous one word, 
        # does not equal to len(self) as the word is not necessarily have a following word
        # ie. bigram != trigram
        self._times = 0 # should be zero for the first word
        self.__p = 0 # should be zero for the first word
        # 1: this word is first word, first word has sublevel of WordDict()
        # 2: this word is second word, second word has sublevel of Three()
        self._levelNum = levelNum
        
    def compute(self, levelTimes):
        if levelTimes:
            self.__p = self._times / levelTimes
        subLevelTimes = 0
        for word in self:
            subLevelTimes += self[word].get_times()
        for word in self:
            self[word].compute(subLevelTimes)
        
    def add(self):
        self._times += 1
    
    def load(self, times, part):
        self._times = times
        if self._levelNum is 1:
            regex_twothreeid_pair = re.compile('[\w:\d]*\[[\w:\d|]*\]') # eat:1[apple:1|orange:1]
            regex_two_threeids = re.compile('([\w:\d]*)\[([\w:\d|]*)\]') # eat:1 and [apple:1|orange:1]
            for pair_twothreeid in regex_twothreeid_pair.findall(part):
                two_counts, threeids = regex_two_threeids.search(pair_twothreeid).groups() 
                two, twoCounts = two_counts.split(':')
                if two not in self:
                    self[two] = WordDict(2) 
                self[two].load(int(twoCounts), threeids)
        if self._levelNum is 2:
            for three_counts in part.split('|'): # apple:1|orange:1
                if len(three_counts.split(':')) is 2:
                    three, threeCounts = three_counts.split(':') # apple:1
                    if three not in self:
                        self[three] = Three()
                    self[three].set_times(int(threeCounts))
    
    # get bigram value [ NOT recommanded ]
    def get_p(self):
        if self._levelNum is not 1:
            return self.__p
        else:
            print('>>> NO P VALUE FOR THE FIRST WORD! <<<')
            return None
            
    def get_times(self):
        return self._times

class TrigramSimple(dict):
    def __init__(self, isReversed = False, isStop = False, isStem = False, default = None):
        dict.__init__(self)
        self.default = default
        self._isReversed = isReversed
        self._isStop = isStop
        self._isStem = isStem
        self.__pre = Preprocessor(isReversed = self._isReversed, isStop = self._isStop, isStem = self._isStem)
    
    # generate filename according to the configurations
    def _getFileName(self, initName):
        filename = initName
        if self._isReversed:
            filename += '_reverse'
        if self._isStop:
            filename += '_stop'
        if self._isStem:
            filename += '_stem'
        filename += '.txt'
        return filename
       
    # get probability value for bigram or trigram [ RECOMMANDED ]
    def get_p(self, one, two, three = None):
        if one is None or two is None:
            return 0
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
    
    def update_line(self, line):
        one = None
        two = None
        line = 'START START ' + line.lower() + ' END END'
        for word in self.__pre.getToken(line):
            if word is None:
                continue
            if two:
                if two not in self:
                    self[two] = WordDict(1)
                if word not in self[two]:
                    self[two][word] = WordDict(2)
                self[two][word].add()
            if one:
                if word not in self[one][two]:
                    self[one][two][word] = Three()
                self[one][two][word].add()
            one = two
            two = word
    
    def update_file(self, filename):
        print('<updating from file....>:\n%s' % filename)
        data = ReadData(filename, True, None)
        TotalLines = data.countLines()
        print('[Total Lines] = ', TotalLines)
        initLineNo = TotalLines/1000
        stepLength = TotalLines/10
        nextLineNo = initLineNo
        iLine = 0
        starttime = time.time()
        for line in data:    
            iLine += 1
            # show progress
            if iLine >= nextLineNo:
                timesofar = (time.time() - starttime) / 60
                totaltime = (timesofar * TotalLines / iLine)
                timeleft = (timesofar * (TotalLines-iLine) / iLine)
                print('[Progress]: %3.2f%% (%d/%d)  %.2f/%.2fmins %.2fmins left' % (iLine/TotalLines*100, iLine, TotalLines, timesofar, totaltime, timeleft))                
                if nextLineNo is initLineNo:
                    nextLineNo = stepLength
                else:
                    nextLineNo += stepLength
            # question lines in the training data
            R21 = re.compile('^21 (.+)\t+([\S]+)\t+([\S]+)$')            
            Qline = R21.search(line)
            if Qline:
                Question = Qline.group(1)
                CorrectAnswer = Qline.group(2)
                # make questions in the training data to be normal sentense
                line = Question.replace('XXXXX', CorrectAnswer) 
            self.update_line(line)
            
    def store(self, initFileName = '.\\Trigram Data\\Trigram'):
        filename = self._getFileName(initFileName)
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
        for one in self:
            self[one].compute(None)
    
    def load(self, initFileName = '.\\Trigram Data\\Trigram'):
        filename = self._getFileName(initFileName)
        print('\t<loading...> : \n\t%s' % basename(filename))
        try:
            indexfile = open(filename,'r')
        except IOError:
            print('FAILURE: INDEX file loading failed!')
            return False
        else:
            regex_one_twothree = re.compile('^([\w]+){(.+)}') # word{....}
            for line in indexfile:
                one, twothree = regex_one_twothree.search(line).groups() # word{....}
                if one not in self:
                    self[one] = WordDict(1)
                self[one].load(0, twothree)
        indexfile.close()
        self.compute()
        print('\t<loaded>')
    
    def answer(self, words_nearby, cand):
        rate_bigram = self.get_p(one = words_nearby[0], two = cand)
        rate_trigram = self.get_p(one = words_nearby[1], two = words_nearby[0],
                                     three = cand)
        return [rate_bigram, rate_trigram]

def Run_BuildData(isStop, isStem, isReversed):
    trainingFiles = [
#                     'CBTest Datasets\CBTest\data\cbt_test.txt',
#                     'CBTest Datasets\CBTest\data\cbt_train.txt',
#                     'CBTest Datasets\CBTest\data\cbt_valid.txt',
                     'CBTest Datasets\CBTest\data\cbtest_CN_valid_2000ex.txt',
                     'CBTest Datasets\CBTest\data\cbtest_NE_valid_2000ex.txt',
                     'CBTest Datasets\CBTest\data\cbtest_P_valid_2000ex.txt',
                     'CBTest Datasets\CBTest\data\cbtest_V_valid_2000ex.txt',
                     'CBTest Datasets\CBTest\data\cbtest_CN_train.txt',
                     'CBTest Datasets\CBTest\data\cbtest_NE_train.txt',
                     'CBTest Datasets\CBTest\data\cbtest_P_train.txt',
                     'CBTest Datasets\CBTest\data\cbtest_V_train.txt'
                    ]
    myTrigram = TrigramSimple(isStop = isStop, isStem = isStem, isReversed = isReversed)
    for file in trainingFiles:
        myTrigram.update_file(file)
    myTrigram.compute()
    myTrigram.store()
    print('<<done!>>')