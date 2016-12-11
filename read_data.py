# -*- coding: utf-8 -*-
"""
Created on Tue Nov 22 15:36:29 2016

@author: ZHULI
"""
import re

def countLines(fileName):
    i = 0 
    file = open(fileName,'r')
    for line in file:
        i += 1
    file.close()
    return i

class ShowProgress():
    def __init__(self, fileName, partNum = 20):
        self.totalLines = countLines(fileName)
        self.iProgress = 0
        self.partNum = partNum
        self.stepLength = int(self.totalLines / self.partNum) 
        self.iLine = 0
        self.nextShowLine = self.stepLength
        self.nextTenPercent = 1
        self.tenPerLines = int(self.totalLines/10)
        self.nextTenPerLine = self.tenPerLines - 1
        
    def update(self):
        self.iLine += 1       
        if self.iLine >= self.nextShowLine:
            self.nextShowLine += self.stepLength
            self.iProgress += 1
            if self.iProgress == self.partNum:
                print(' ok') # finishing
                return
            if self.iLine > self.nextTenPerLine:
                while  self.iLine > self.nextTenPerLine:
                    print(self.nextTenPercent, end = '')
                    self.nextTenPercent += 1
                    self.nextTenPerLine += self.tenPerLines
            else:
                print('.', end = '')
            

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
        return countLines(self.filename)
        
    def _ReadTrainingData(self):
        TrainingData = open(self.filename,'r')
        for line in TrainingData:
            # text line
            yield line
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

    