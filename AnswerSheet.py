# -*- coding: utf-8 -*-
"""
Created on Wed Dec 8 16:36:45 2016

@author: ZHULI
"""

import os, time, sys, numpy as np
from os.path import basename

# questionNum:approachID:Rates
class AnswerSheet_oneTestFile(dict):
    def __init__(self, isStop, isStem, fileName):
        self.__testName = basename(fileName).split('.')[0]
        self.__isStop = isStop
        self.__isStem = isStem
        self.__approaches_NameID = {}
        self.__correctAnsID = -1 # correctAns approachID = -1
        self.__mixedRatesID = -2 # mixedRates approachID = -2
    
    def reg_Approach(self, approachName):
        if approachName not in self.__approaches_NameID.keys():
            approachID = len(self.__approaches_NameID.keys())
            self.__approaches_NameID[approachName] = approachID
            return approachID
        else:
            return self.__approaches_NameID[approachName]
    
    def getApproachName(self, approachID):
        for Name in self.__approaches_NameID.keys():
            if approachID == self.__approaches_NameID[Name]:
                return Name
        return None
          
    def reg_newQuestion(self, questionNum, correctAnswer, candidates):
        # find correct answer index
        candidatesList = list(filter(None ,candidates.split('|')))
        if correctAnswer not in candidatesList:
            print('[ERROR] cannot find correct answer index')
            print('QuestionNum =', questionNum)
            print('correctAnswer =', correctAnswer)
            print('candidates = ', candidates)
            sys.exit()
        else:
            correctAnsIndex = candidatesList.index(correctAnswer)
        # record the correct answer index
        if questionNum not in self.keys():
            self[questionNum] = {}
        else:
            if self.__correctAnsID in self[questionNum].keys():
                if self[questionNum][self.__correctAnsID] != correctAnsIndex:
                    print('[ERROR] different correct answer index')
                    print('QuestionNum =', questionNum)
                    print('correctAnswer =', correctAnswer)
                    print('candidates = ', candidates)
                    print('old index = ', self[questionNum][self.__correctAnsID])
                    print('new index = ', correctAnsIndex)
                    sys.exit()
        self[questionNum][self.__correctAnsID] = correctAnsIndex
        
    def submit_rates(self, questionNum, approachID, ratesList):
        if approachID not in self.__approaches_NameID.values():
            print('[ERROR] please register the approach first')
            sys.exit()
        if questionNum not in self:
            print('[WARNING] please register the question first')
            sys.exit()
        self[questionNum][approachID] = ratesList

    def __writeApproachResult(self, approachName, approachID, lineFormat, file):
        attemptNum = 0
        correctNum = 0
        for qNum in self.keys():
            if approachID in self[qNum].keys():                
                maxRate = np.max(self[qNum][approachID])
                if maxRate > 0:
                    attemptNum += 1 # if maxRate =0, consider as not attempted
                    choice = self[qNum][approachID].index(maxRate)
                    if self.__correctAnsID not in self[qNum]:
                        print('[ERROR] No correct answer recorded for Qunestion Num', qNum)
                        sys.exit()
                    # compare to correct answer
                    if choice == self[qNum][self.__correctAnsID]:
                        correctNum += 1
        # write to file
        mytime = time.ctime()
        accuracy_overall = 0
        accuracy_attempted = 0        
        totalQuestionNum = len(self.keys())
        if totalQuestionNum > 0:
            accuracy_overall = correctNum/totalQuestionNum
        if attemptNum > 0:
            accuracy_attempted = correctNum/attemptNum
        accuracy_overall = str('{:.6f}'.format(round(accuracy_overall, 6)))
        ratio_overall = '('+str(correctNum)+'/'+str(totalQuestionNum)+')'
        accuracy_attempted = str('{:.6f}'.format(round(accuracy_attempted, 6)))
        ratio_attempted = '('+str(correctNum)+'/'+str(attemptNum)+')'
        print(lineFormat % (mytime, self.__isStop, self.__isStem,
                            accuracy_overall, ratio_overall,
                            accuracy_attempted, ratio_attempted, self.__testName, approachName), file = file)
        
    def printToFile(self, filename = 'Results.txt'):
        # open file
        lineFormat = '%24s\t%6s\t%6s\t%+10s\t%+10s\t%+10s\t%+10s\t%25s\t%-25s'
        if os.path.isfile('Results.txt') is False:
            file = open(filename, 'w')
            print(lineFormat%('Time', 'isStop', 'isStem', 'Overall', '', 'Attempted', '', 'Test', 'Approach'), file = file)
        else:
            file = open(filename, 'a')
        # write the results of approaches
        approachNameList = sorted(list(str(k) for k in self.__approaches_NameID.keys()))
        for approachName in approachNameList:
            approachID = self.__approaches_NameID[approachName]
            self.__writeApproachResult(approachName, approachID, lineFormat, file)
        # update mixed rates
        for qNum in self.keys():
            # clear mixed rates
            self[qNum][self.__mixedRatesID] = [0.0 for i in range(10)]
            for approachID in self[qNum]:
                if approachID != self.__mixedRatesID and approachID != self.__correctAnsID:
                    self[qNum][self.__mixedRatesID] = [x+y for x, y in zip(self[qNum][self.__mixedRatesID], self[qNum][approachID])]
        # write for mixed rates
        self.__writeApproachResult('All Approaches', self.__mixedRatesID, lineFormat, file)
        print(file = file)
        file.close()