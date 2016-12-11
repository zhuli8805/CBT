# -*- coding: utf-8 -*-
"""
Created on Tue Nov 22 13:27:19 2016

@author: ZHULI
"""

import re, numpy as np
from read_data import ShowProgress
from TrigramSimple import TrigramSimple, Preprocessor
from TrigramWP import TrigramWP
from os.path import basename

Regex_POS = re.compile(':[\w$]+')

class TrigramPairWP(): 
    # _modelA is a NON REVERSED model
    # _modelB is a REVERSED model
    def __init__(self, isPOS, isStop, isStem, w = [1, 1, 1, 1]):
        self._isPOS = isPOS
        self._isStop = isStop
        self._isStem = isStem
        self.__w = w
        self.__approaches = []
        # using WP index file
        self._modelA = TrigramWP(isPOS = isPOS, isReversed = False, isStop = isStop, isStem = isStem)
        self._modelB = TrigramWP(isPOS = isPOS, isReversed = True, isStop = isStop, isStem = isStem)
        # MUST NOT load if this is a model based on context
        if type(self) == TrigramPairWP: 
            self._modelA.load()
            self._modelB.load()
            
    def reg_toAnswerSheet(self, answerSheet):
        if self._isPOS:
            self.__approaches = ['PP', 'PW', 'Pmixed']
        else:
            self.__approaches = ['WW', 'WP', 'Wmixed']
        for i in range(3):
            if type(self) == TrigramPairWP: 
                self.__approaches[i] = 'TrigramWP train ' + self.__approaches[i]
            else:
                self.__approaches[i] = 'TrigramWP 20 ' + self.__approaches[i]
            # Name -> ID
            self.__approaches[i] = answerSheet.reg_Approach(self.__approaches[i])
        return answerSheet
        
        # return rates of all ten candidates
        # inputs are W:P (except the correctAnswer)
    def answer(self, iQuestion, wordPOS_nearby, candidatesList, myAnswerSheet):    
        # preprocess: split word:POS
        main_nearby = []
        alter_nearby = []
        for wp in wordPOS_nearby:
            if self._isPOS:
                alter, main = wp.split(':')
            else:
                main, alter = wp.split(':')
            main_nearby.append(main)
            alter_nearby.append(alter)
        # get the rates of each candidate NOTE: candidateList and cand are in the form of W:P 
        ratesList_MM = [] # word to word or POS to POS
        ratesList_MA = [] # word to POS or POS to word
        ratesList_mixed = [] # mix
        for cand in candidatesList:
            if self._isPOS:
                cand_alter, cand_main = cand.split(':')
            else:
                cand_main, cand_alter = cand.split(':')
            # rate MM
            rate_MM = self._modelA.answer([main_nearby[0], main_nearby[1]], cand_main)
            rate_MM += self._modelB.answer([main_nearby[2], main_nearby[3]], cand_main)
            rate_MM = np.dot(self.__w, rate_MM)   
            ratesList_MM.append(rate_MM)
            # rate MA
            rate_MA = self._modelA.answer_alter([main_nearby[0], main_nearby[1]], cand_alter)
            rate_MA += self._modelB.answer_alter([main_nearby[2], main_nearby[3]], cand_alter)
            rate_MA = np.dot(self.__w, rate_MA)   
            ratesList_MA.append(rate_MA)
            # mixed
            ratesList_mixed.append(rate_MM + rate_MA)
        # submit rates to answer sheet
        myAnswerSheet.submit_rates(iQuestion, self.__approaches[0], ratesList_MM)
        myAnswerSheet.submit_rates(iQuestion, self.__approaches[1], ratesList_MA)
        myAnswerSheet.submit_rates(iQuestion, self.__approaches[2], ratesList_mixed)
        return myAnswerSheet, ratesList_MM, ratesList_MA, ratesList_mixed
        
class TrigramPairWP_20(TrigramPairWP):
    def update_line(self, line):
        self._modelA.update_line(line)
        self._modelB.update_line(line)
    
    def compute(self):
        self._modelA.compute()
        self._modelB.compute()
        
    def reset_index(self):
        self._modelA = TrigramWP(isPOS = self._isPOS, isReversed = False, isStop = self._isStop, isStem = self._isStem)
        self._modelB = TrigramWP(isPOS = self._isPOS, isReversed = True, isStop = self._isStop, isStem = self._isStem)
    
# answer the questions using the test_WP.txt files
def answer_Trigram_WP(isStop, isStem, testDict):
    print('[Trigram WP]: isStop = ', isStop,' , isStem = ', isStem)
    TP_list = []
    TP_list.append(TrigramPairWP(isPOS = False, isStop = isStop, isStem = isStem))
    TP_list.append(TrigramPairWP(isPOS = True, isStop = isStop, isStem = isStem))
    TP20_list = []
    TP20_list.append(TrigramPairWP_20(isPOS = False, isStop = isStop, isStem = isStem))
    TP20_list.append(TrigramPairWP_20(isPOS = True, isStop = isStop, isStem = isStem))
    RLineNum = re.compile('^\d+')
    R21 = re.compile('^21\t+(.+)\t+([\S]+)\t+([\S]+)$')
    approachID_List = []
    for fileName in [f for f in testDict.keys()]:
        myAnswerSheet = testDict[fileName]
        fileName = fileName.replace('.txt', '_WP.txt')
        for tp20 in TP20_list:
            tp20.reset_index()
        for triPair in TP_list + TP20_list:
            myAnswerSheet = triPair.reg_toAnswerSheet(myAnswerSheet)
        # register approach to answer sheet
        approachID_List.append(myAnswerSheet.reg_Approach('TrigramWP MM'))
        approachID_List.append(myAnswerSheet.reg_Approach('TrigramWP MA'))
        approachID_List.append(myAnswerSheet.reg_Approach('TrigramWP mixed'))
        # read file
        iQuestion = 0
        progress = ShowProgress(fileName)
        print('\t -->', basename(fileName), end = ' ')
        file = open(fileName,'r')        
        for line in file:
            # show progress
            progress.update()
            # answer
            mLineNum = RLineNum.search(line)
            if mLineNum:
                if int(mLineNum.group(0)) != 21:
                    #20 sentences
                    for tp20 in TP20_list:
                        tp20.update_line(line)
                else:
                    iQuestion += 1
                    # compute for context
                    for triPair in TP20_list:
                        triPair.compute()
                    #21st sentence (Question)
                    m21 = R21.search(line)
                    question = m21.group(1)
                    correctAnswer = m21.group(2)
                    candidates = m21.group(3)   
                    myAnswerSheet.reg_newQuestion(iQuestion, correctAnswer, candidates)                    
                    # add START and END
                    question = 'START:START START:START ' + question + ' END:END END:END'
                    # find the surrounding words
                    wordPOS_nearby = []
                    Regex_XXXXX = re.compile('XXXXX[:\w]*') # find the index of XXXXX in the question
                    XXXXX = Regex_XXXXX.search(question).group(0)
                    wordsinQestion = question.split(' ')
                    iXXXXX = wordsinQestion.index(XXXXX)
                    wordPOS_nearby.append(wordsinQestion[iXXXXX - 1]) # bigram
                    wordPOS_nearby.append(wordsinQestion[iXXXXX - 2]) # trigram
                    wordPOS_nearby.append(wordsinQestion[iXXXXX + 1]) # reversed bigram
                    wordPOS_nearby.append(wordsinQestion[iXXXXX + 2]) # reversed trigram
                    # make candidates a list
                    candidatesList = list(filter(None ,candidates.split('|')))
                    totalRates_MM = [0 for i  in range(10)]
                    totalRates_MA = [0 for i  in range(10)]
                    totalRates_mixed = [0 for i  in range(10)]
                    for triPair in TP_list + TP20_list:
                        myAnswerSheet, ratesList_MM, ratesList_MA, ratesList_mixed = triPair.answer(iQuestion, wordPOS_nearby, candidatesList, myAnswerSheet)
                        totalRates_MM = [x+y for x, y in zip(totalRates_MM, ratesList_MM)]
                        totalRates_MA = [x+y for x, y in zip(totalRates_MA, ratesList_MA)]
                        totalRates_mixed = [x+y for x, y in zip(totalRates_mixed, ratesList_mixed)]
                    myAnswerSheet.submit_rates(iQuestion, approachID_List[0], totalRates_MM)
                    myAnswerSheet.submit_rates(iQuestion, approachID_List[1], totalRates_MA)
                    myAnswerSheet.submit_rates(iQuestion, approachID_List[2], totalRates_mixed)
            else:
                #blank line, Reset
                for tp20 in TP20_list:
                    tp20.reset_index()
        file.close()
    return testDict
       
# answer the questions by reading the original test.txt (simple Trigram Model only)
def answer_Trigram_simple(isStop, isStem, testDict):
    print('[Trigram Simple]: isStop = ', isStop,' , isStem = ', isStem)
    myPreprocessor = Preprocessor(isStop = isStop, isStem = isStem)
    Trigram = TrigramSimple(isStop = isStop, isStem = isStem, isReversed = False)
    Trigram.load()
    Trigram_r = TrigramSimple(isStop = isStop, isStem = isStem, isReversed = True)
    Trigram_r.load()
    Trigram20 = TrigramSimple(isStop = isStop, isStem = isStem, isReversed = False)
    Trigram20_r = TrigramSimple(isStop = isStop, isStem = isStem, isReversed = True)
    
    RLineNum = re.compile('^\d+')
    R21 = re.compile('^\d+ (.+)\t+([\S]+)\t+([\S]+)$')
    RWord = re.compile('\w+')
    w_train = [1, 1, 1, 1] # -1, -2, 1, 2
    w_20 = [1, 1, 1, 1] # -1, -2, 1, 2    
    for fileName in testDict.keys():
        myAnswerSheet = testDict[fileName]
        print('\t -->', basename(fileName), end = '')
        file = open(fileName,'r')        
        ApproachID_train = myAnswerSheet.reg_Approach('Trigram Simple trian')
        ApproachID_20 = myAnswerSheet.reg_Approach('Trigram Simple 20')
        ApproachID_mixed = myAnswerSheet.reg_Approach('Trigram Simple trian&20')
        iQuestion = 0
        progress = ShowProgress(fileName)
        for line in file:
            # show progress
            progress.update()
            # answer
            mLineNum = RLineNum.search(line)
            if mLineNum:
                if int(mLineNum.group(0)) != 21:
                    #20 sentences
                    Trigram20.update_line(line)
                    Trigram20_r.update_line(line)
                    continue
                else:
                    iQuestion += 1
                    Trigram20.compute()
                    Trigram20_r.compute()
                    #21st sentence ( Question )
                    m21 = R21.search(line.lower())
                    Question = m21.group(1)
                    candidates = m21.group(3)
                    correctAnswer = m21.group(2)
                    myAnswerSheet.reg_newQuestion(iQuestion, correctAnswer, candidates)
                    # find the surrounding words
                    words_nearby = [] # prev and next 2 words
                    Question = 'START START ' + myPreprocessor.getLine(Question.lower()) + ' END END'
                    WordsinQestion = RWord.findall(Question)
                    ixxxxx = WordsinQestion.index('xxxxx')
                    words_nearby.append(WordsinQestion[ixxxxx - 1])
                    words_nearby.append(WordsinQestion[ixxxxx - 2])
                    words_nearby.append(WordsinQestion[ixxxxx + 1])
                    words_nearby.append(WordsinQestion[ixxxxx + 2])
                    # rate ten candidates
                    ratesList_train = []
                    ratesList_20 = []
                    ratesList_mixed = []
                    candidatesList = list(filter(None ,candidates.split('|')))
                    for cand in candidatesList:
                        # train
                        rate_train = Trigram.answer([words_nearby[0], words_nearby[1]], cand)
                        rate_train += Trigram_r.answer([words_nearby[2], words_nearby[3]], cand)
                        rate_train = np.dot(rate_train, w_train)
                        ratesList_train.append(rate_train)
                        # 20
                        rate_20 = Trigram20.answer([words_nearby[0], words_nearby[1]], cand)
                        rate_20 += Trigram20_r.answer([words_nearby[2], words_nearby[3]], cand)
                        rate_20 = np.dot(rate_20, w_20)
                        ratesList_20.append(rate_20)
                        # mixed
                        ratesList_mixed.append(rate_train + rate_20)
                    # submit rates to answer sheet
                    myAnswerSheet.submit_rates(iQuestion, ApproachID_train, ratesList_train)
                    myAnswerSheet.submit_rates(iQuestion, ApproachID_20, ratesList_20)
                    myAnswerSheet.submit_rates(iQuestion, ApproachID_mixed, ratesList_mixed)
            else:
                #blank line,  Reset
                Trigram20 = TrigramSimple(isStop = isStop, isStem = isStem, isReversed = False)
                Trigram20_r = TrigramSimple(isStop = isStop, isStem = isStem, isReversed = True)
                continue
        file.close()
    return testDict