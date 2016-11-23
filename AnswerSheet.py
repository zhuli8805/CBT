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
        
    def newQuestion(self, correctAnswer):
        self.__correctAnswer = correctAnswer
        self.__totalQuestionNum += 1
        
    def submitAnswer(self, myAnswer):
        if myAnswer is self.__correctAnswer:
            self.__correctAnswerNum += 1
        self.__correctAnswer = None
    
    def printResult(self):
        print('Score = %3.3f ( %d / %d )' % (self.__correctAnswerNum/self.__totalQuestionNum, 
              self.__correctAnswerNum, self.__totalQuestionNum))
        
    def reset(self):
        self.__correctAnswer = None
        self.__totalQuestionNum = 0
        self.__correctAnswerNum = 0