# -*- coding: utf-8 -*-
"""
Created on Tue Nov 22 16:36:45 2016

@author: ZHULI
"""

import os, time, re

class AnswerSheet():
    def __init__(self, isStop, isStem, testFileName = None):
        self.set_filename(testFileName)
        self.__correctAnswer = None
        self.__totalQuestionNum = 0
        self.__correctAnswerNum = 0
        self.__answersMade = 0
        self.__isStop = isStop
        self.__isStem = isStem
        
    def newQuestion(self, correctAnswer):
        self.__correctAnswer = correctAnswer
        self.__totalQuestionNum += 1
#        print('CorrectAnswer = ', correctAnswer)
        
    def submitAnswer(self, myAnswer):
        if myAnswer:
            self.__answersMade += 1
            result = myAnswer == self.__correctAnswer
            if result:
                self.__correctAnswerNum += 1
#            print('<%s> vs <%s>' % (myAnswer, self.__correctAnswer), result)
#            print('=============================')
            self.__correctAnswer = None
        else:
            self.__correctAnswer = None
        
    def printResult(self):
        if self.__totalQuestionNum != 0:
            print('[Overall Score] = %3.3f ( %d / %d )' % (self.__correctAnswerNum/self.__totalQuestionNum, 
                  self.__correctAnswerNum, self.__totalQuestionNum))
        else:
            print('No question was asked')
            
        if self.__answersMade != 0:
            print('[Score of attempted questions] = %3.3f ( %d / %d )' % (self.__correctAnswerNum/self.__answersMade, 
                  self.__correctAnswerNum, self.__answersMade))
        else:
            print('No question was attempted')
       
    def set_filename(self, filename):
        filename = filename.split('\\').pop().replace('.txt', '')
        if filename is None:
            self.__testName = None
        Regex_testname = re.compile('\\\([\w_0-9]*?).txt')
        res = Regex_testname.findall(filename)
        if res:
            self.__testName = res[0]
        else:
            self.__testName = filename
    
    def printToFile(self, comments, filename = 'Results.txt'):
        if os.path.isfile('Results.txt') is False:
            file = open(filename, 'w')    
            print('%24s\t%5s\t%5s\t%s\t\t\t\t\t\t%5s\t\t\t%16s\t\t\t%8s'
            %('Time', 'isStop', 'isStem', 'Overall', 'Attempted', 'Test Name', 'Comments'), file = file)
        else:
            file = open(filename, 'a')
        mytime = time.ctime()
        overall = None
        attempted = None
        if self.__totalQuestionNum > 0:
            overall = self.__correctAnswerNum/self.__totalQuestionNum * 100
        if self.__answersMade > 0:
            attempted = self.__correctAnswerNum/self.__answersMade * 100
        print('%24s\t%5s\t%5s\t%3.5f%%\t(%d/%d)\t\t%3.5f%%\t(%d/%d)\t' 
        % (mytime, self.__isStop, self.__isStem, overall, self.__correctAnswerNum, self.__totalQuestionNum ,attempted, self.__correctAnswerNum, self.__answersMade)
        + self.__testName + '  ' + comments , file = file)
        file.close()
        
    def reset(self, testFileName = None):
        self.set_filename(testFileName)
        self.__correctAnswer = None
        self.__totalQuestionNum = 0
        self.__correctAnswerNum = 0
        self.__answersMade = 0
        
    def get_score(self):
        overallScore = None
        attemptedScore = None
        if self.__totalQuestionNum > 0:
            overallScore = self.__correctAnswerNum/self.__totalQuestionNum
        if self.__answersMade > 0 :
            attemptedScore = self.__correctAnswerNum/self.__answersMade
        return overallScore, attemptedScore