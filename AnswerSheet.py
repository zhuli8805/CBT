# -*- coding: utf-8 -*-
"""
Created on Tue Nov 22 16:36:45 2016

@author: ZHULI
"""

class AnswerSheet():
    def __init__(self, filename):
        self.testName = filename
        self.__correctAnswer = None
        self.__totalQuestionNum = 0
        self.__correctAnswerNum = 0
        self.__answersMade = 0
        
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
        
    def reset(self):
        self.__correctAnswer = None
        self.__totalQuestionNum = 0
        self.__correctAnswerNum = 0
        
    def get_score(self):
        overallScore = None
        attemptedScore = None
        if self.__totalQuestionNum > 0:
            overallScore = self.__correctAnswerNum/self.__totalQuestionNum
        if self.__answersMade > 0 :
            attemptedScore = self.__correctAnswerNum/self.__answersMade
        return overallScore, attemptedScore