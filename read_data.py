# -*- coding: utf-8 -*-
"""
Created on Tue Nov 22 15:36:29 2016

@author: ZHULI
"""
import re

class ReadData():
    def __init__(self, filename, isTraining, pAnswerSheet):
        self.isTraining = isTraining
        self.filename = filename
        self.pAnswerSheet = pAnswerSheet
        
    def __iter__(self):
        if self.isTraining:
            for line in self._ReadTrainingData():
                yield line
        else:
            for line in self._ReadTestData():
                yield line
    
    def countLines(self):
        i = 0 
        TrainingData = open(self.filename,'r')
        for line in TrainingData:
            i += 1
        TrainingData.close()
        return i
        
    def _ReadTrainingData(self):      
#        print('Reading Training Data :\n %s' % (self.filename))
        TrainingData = open(self.filename,'r')
#        Regex_BookTitle = re.compile('_BOOK_TITLE_ : (.+).txt.out')
        for line in TrainingData:
            # text line
            yield line
            # book title line
#            res_reg = Regex_BookTitle.search(line)
#            if res_reg:
#                filename_temp = self.filename.split('\\')
#                filename_temp = filename_temp[len(filename_temp) - 1]
##                print('Read Training Data[%s] :\n %s' % (filename_temp, res_reg.group(1)))
#                continue            
        TrainingData.close()

    def _ReadTestData(self):
        RLineNum = re.compile('^\d+')
        R20 = re.compile('^\d+ (.*)')
        R21 = re.compile('^\d+ (.+)\t+([\S]+)\t+([\S]+)$')
        TrainingData = open(self.filename,'r')
        for line in TrainingData:
            mLineNum = RLineNum.search(line)
            if(mLineNum):
                print (mLineNum)
                if(int(mLineNum.group(0)) < 21):
                    # 20 sentences
                    sentence = R20.search(line).group(1)                    
                    yield False, sentence
                else:
                    # 21st sentence
                    m21 = R21.search(line)
                    Question = m21.group(1)
                    Candidates = m21.group(3).split('|')
                    CorrectAnswer = m21.group(2)
                    if self.pAnswerSheet:
                        self.pAnswerSheet[0].newQuestion(CorrectAnswer)
                    yield True, [Question, Candidates]
            else:
                #blank line
            
                continue
        TrainingData.close()
        
## test code
#filename = '..\..\..\..\CBTest Datasets\CBTest\data\cbt_train.txt'
#rd = ReadData(filename, True, None)
#for line in rd:
##    print(line)
#    pass