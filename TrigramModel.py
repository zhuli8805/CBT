# -*- coding: utf-8 -*-
"""
Created on Tue Nov 22 14:39:42 2016

@author: ZHULI
"""

import re, time
from read_data import ReadData
from Preprocessor import Preprocessor

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
            if word not in ['START', 'END']: 
                subLevelTimes += self[word].get_times()
        for word in self:
            if word not in ['START', 'END']:
                self[word].compute(subLevelTimes)
        
    def add(self):
#        print('WordDict self.__times old==', self.__times)
        self.__times += 1
#        print('WordDict self.__times==', self.__times)
    
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
    def get_p(self):
        if self.__levelNum is not 1:
            return self.__p
        else:
            print('>>> NO P VALUE FOR THE FIRST WORD! <<<')
            return None
            
    def get_times(self):
        return self.__times

class TrigramModel(dict):
    def __init__(self, isReversed = False, isStop = False, isStem = False, default = None):
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
        print('<loading...> : \n%s' % filename)
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
        print('<loaded>')
    
    def answer(self):
        pass

def Run_BuildData(isStop, isStem, isReversed):
    trainingFiles = [
#                     '..\..\..\..\CBTest Datasets\CBTest\data\cbt_test.txt',
#                     '..\..\..\..\CBTest Datasets\CBTest\data\cbt_train.txt'],
#                     '..\..\..\..\CBTest Datasets\CBTest\data\cbt_valid.txt',
                     '..\..\..\..\CBTest Datasets\CBTest\data\cbtest_CN_train.txt',
                     '..\..\..\..\CBTest Datasets\CBTest\data\cbtest_NE_train.txt',
                     '..\..\..\..\CBTest Datasets\CBTest\data\cbtest_P_train.txt',
                     '..\..\..\..\CBTest Datasets\CBTest\data\cbtest_V_train.txt'
                    ]

    myTrigram = TrigramModel(isStop = isStop, isStem = isStem, isReversed = isReversed)
    for file in trainingFiles:
        myTrigram.update_file(file)
    myTrigram.compute()
    myTrigram.store()
    print('<<done!>>')
    
    # Data test
#    print(test.get_p('our', 'family')) # recommanded way for bigram p
#    print(test.get_p('my', 'dear')) # recommanded way for trigram p 
#    print(test['our']['family'].get_times())


#Run_buildData(isStop = True, isStem = True, isReversed = False)
#Run_buildData(isStop = True, isStem = True, isReversed = True)
#Run_buildData(isStop = True, isStem = False, isReversed = False)
#Run_buildData(isStop = True, isStem = False, isReversed = True)
#Run_buildData(isStop = False, isStem = True, isReversed = False)
#Run_buildData(isStop = False, isStem = True, isReversed = True)
#Run_buildData(isStop = False, isStem = False, isReversed = False)
#Run_buildData(isStop = False, isStem = False, isReversed = True)


### loading result test
#test2 = TrigramModel(isStop = False, isStem = False, isReversed = False)
#test2.load()
#print(test2.get_p('our', 'family')) # recommanded way for bigram p
#print(test2.get_p('my', 'dear')) # recommanded way for trigram p 
#print(test2['our']['family'].get_times())