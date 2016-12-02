# -*- coding: utf-8 -*-
#import sys
#sys.setdefaultencoding('utf8')
#sys.getdefaultencoding()
"""
Created on Tue Nov 22 13:27:19 2016

@author: ZHULI
"""

import re, numpy as np
from AnswerSheet import AnswerSheet
from TrigramModel import TrigramModel, Preprocessor
from TrigramModel_WP import TrigramModel_WP

class TrigramPair(): 
    # __modelA is a NON REVERSED model
    # __modelB is a REVERSED model
    def __init__(self, isWP, isPOS, isStop, isStem, testFileName = None, wA = [1, 1, 1, 1], wB = [1, 1, 1, 1]):
        self.answersheet = AnswerSheet(isStop = isStop, isStem = isStem, testFileName = testFileName)
        self.__isWP = isWP
        self.__wA = wA
        self.__wB = wB
        if self.__isWP:
            self.__modelA = TrigramModel_WP(isPOS = isPOS, isReversed = False, isStop = isStop, isStem = isStem)
            self.__modelB = TrigramModel_WP(isPOS = isPOS, isReversed = True, isStop = isStop, isStem = isStem)
        else:
            self.__modelA = TrigramModel(isReversed = False, isStop = isStop, isStem = isStem)
            self.__modelB = TrigramModel(isReversed = True, isStop = isStop, isStem = isStem)
        self.__modelA.load()
        self.__modelB.load()
        
    def rate(self, question, candidates):
        ratingA = self.__modelA.answer(question, candidates)
        ratingB = self.__modelB.answer(question, candidates)
        ratings = ratingA + ratingB
        return ratings
        
    def update_line(self, line):
        pass
        
    def answer(self, correctAnswer, question, candidates):
        rate_allCands = []
        Regex_POS = re.compile(':[\w$]+')
#        # pure word wanted for correct answer
#        for P in Regex_POS.findall(correctAnswer):
#            correctAnswer.replace(P, '')
        self.answersheet.newQuestion(correctAnswer)
        # if not word/pos remove the POS tags 
        question = 'START:START START:START ' + question + ' END:END END:END'
        if self.__isWP is False:
            for P in Regex_POS.findall(question):
                question.replace(P, '')
            for P in Regex_POS.findall(candidates):
                candidates.replace(P, '')
        words_nearby = []        
        # find the index of XXXXX in the question
        Regex_XXXXX = re.compile('XXXXX[:\w]*')
        XXXXX = Regex_XXXXX.search(question).group(1)
        # find the surrounding words
        wordsinQestion = question.split(' ')
        iXXXXX = wordsinQestion.index(XXXXX)
        words_nearby.append(wordsinQestion[iXXXXX - 1])
        words_nearby.append(wordsinQestion[iXXXXX - 2])
        words_nearby.append(wordsinQestion[iXXXXX + 1])
        words_nearby.append(wordsinQestion[iXXXXX + 2])
        # candidate list
        candidateList = candidates.split('|')
        # get the rates of the each candidate
        for cand in candidateList:
            rate_oneCand = 0
            rate_oneCand += np.dot(self.__wA, self.__modelA.rate_oneCand(question, cand))
            rate_oneCand += np.dot(self.__wB, self.__modelB.rate_oneCand(question, cand))
            rate_allCands.append(rate_oneCand)
        maxrate = np.max(rate_allCands)
        if maxrate == 0:
            self.answersheet.submitAnswer(None)
        else:
            imax = rate_allCands.index(maxrate)
            myAnswer = candidateList[imax]            
            self.answersheet.submitAnswer(myAnswer)
        return rate_allCands
    
    def reset(self, testFileName):
        self.answersheet.reset(testFileName = testFileName)
        
class TrigramPair_20(TrigramPair):
    def __init__(self, isWP, isPOS, isStop, isStem, testFileName = None, wA = [1, 1, 1, 1], wB = [1, 1, 1, 1]):
        self.answersheet = AnswerSheet(isStop = isStop, isStem = isStem, testFileName = testFileName)
        self.__isWP = isWP
        self.__isPOS = isPOS
        self.__isStop = isStop
        self.__isStem = isStem
        if self.__isWP:
            self.__modelA = TrigramModel_WP(isPOS = isPOS, isReversed = False, isStop = isStop, isStem = isStem)
            self.__modelB = TrigramModel_WP(isPOS = isPOS, isReversed = True, isStop = isStop, isStem = isStem)
        else:
            self.__modelA = TrigramModel(isReversed = False, isStop = isStop, isStem = isStem)
            self.__modelB = TrigramModel(isReversed = True, isStop = isStop, isStem = isStem)
        
    def update_line(self, line):
        pass
    
    def reset(self):
        TrigramPair.reset(self)
        if self.__isWP:
            self.__modelA = TrigramModel_WP(isPOS = self.__isPOS, isReversed = False, isStop = self.__isStop, isStem = self.__isStem)
            self.__modelB = TrigramModel_WP(isPOS = self.__isPOS, isReversed = True, isStop = self.__isStop, isStem = self.__isStem)
        else:
            self.__modelA = TrigramModel(isReversed = False, isStop = self.__isStop, isStem = self.__isStem)
            self.__modelB = TrigramModel(isReversed = True, isStop = self.__isStop, isStem = self.__isStem)
         
# answer the questions by reading the test_WP.txt files
def run_Trigram_WP(isStop, isStem, filename):
    TP_list = []    
    TP_list.append(TrigramPair(isWP = True, isPOS = True, isStop = isStop, isStem = isStem, testFileName = filename))
    TP20_list = []
    RLineNum = re.compile('^\d+')
    R21 = re.compile('^\d+ (.+)\t+([^\t]+)\t+([^\t]+)$')    
    file = open(filename,'r')
    myAnswerSheet_mixed = AnswerSheet(isStop = isStop, isStem = isStem, filename = filename)    
    for line in file:
        mLineNum = RLineNum.search(line)
        if mLineNum:
            if int(mLineNum.group(0)) != 21:
                #20 sentences
                for tp20 in TP20_list:
                    tp20.update_line(line)
            else:
                #21st sentence ( Question )
                m21 = R21.search(line)
                question = m21.group(1)
                candidates = m21.group(3)
                correctAnswer = m21.group(2)
                # make correct answer original
                Regex_POS = re.compile(':[\w$]+')
                for P in Regex_POS.findall(correctAnswer):
                    correctAnswer.replace(P, '')                                
                myAnswerSheet_mixed.newQuestion(correctAnswer)
                rate_allCands_mixed = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                for triPair in TP_list + TP20_list:
                    ratelist = triPair.answer(correctAnswer = correctAnswer, question = question, candidates = candidates)
                    rate_allCands_mixed = [x+y for x, y in zip(rate_allCands_mixed, ratelist)]
                # choose the top rated candidate for answer                
                maxrate = np.max(rate_allCands_mixed)
                if maxrate == 0:
                    myAnswerSheet_mixed.submitAnswer(None)
                else:
                    imax = rate_allCands_mixed.index(maxrate)
                    # candidate list
                    for P in Regex_POS.findall(candidates):
                        candidates.replace(P, '')
                    candidateList = candidates.split('|')
                    myAnswer = candidateList[imax]  
                    myAnswerSheet_mixed.submitAnswer(myAnswer)                        
        else:
            #blank line, Reset
            for tp20 in TP20_list:
                tp20.reset()
    file.close()
    print('--Overall Answersheet---')
    myAnswerSheet_mixed.printResult()
    myAnswerSheet_mixed.printToFile('Overall')
    for triPair in TP_list + TP20_list:
        triPair.answersheet.printToFile('Overall')
    print('----------------------')
    
       
# answer the questions by reading the original test.txt (simple Trigram Model only)
def answer_Trigramsimple(isStop, isStem, filename):
    print('Run Trigram test: isStop = ', isStop,' , isStem = ', isStem)
    print('[File Name] = ', filename)
    myPreprocessor = Preprocessor(isStop = isStop, isStem = isStem)
    Trigram = TrigramModel(isStop = isStop, isStem = isStem, isReversed = False)
    Trigram.load()
    Trigram_r = TrigramModel(isStop = isStop, isStem = isStem, isReversed = True)
    Trigram_r.load()
    Trigram20 = TrigramModel(isStop = isStop, isStem = isStem, isReversed = False)
    Trigram20_r = TrigramModel(isStop = isStop, isStem = isStem, isReversed = True)
    
    RLineNum = re.compile('^\d+')
    R21 = re.compile('^\d+ (.+)\t+([\S]+)\t+([\S]+)$')
    RWord = re.compile('\w+')
    w_corpus = [1, 1, 1, 1] # -2, -1, 1, 2
    w_20 = [1, 1, 1, 1] # -2, -1, 1, 2
    
    file = open(filename,'r')
    myAnswerSheet_mixed = AnswerSheet(isStop = isStop, isStem = isStem, filename = filename)
    myAnswerSheet_corpus = AnswerSheet(isStop = isStop, isStem = isStem, filename = filename)
    myAnswerSheet_20 = AnswerSheet(isStop = isStop, isStem = isStem, filename = filename)
    
    for line in file:
        mLineNum = RLineNum.search(line)
        if mLineNum:
            if int(mLineNum.group(0)) != 21:
                #20 sentences
                Trigram20.update_line(line)
                Trigram20_r.update_line(line)
                continue
            else:
                #21st sentence ( Question )
                m21 = R21.search(line.lower())
                Question = m21.group(1)
                Candidates = m21.group(3).split('|')
                CorrectAnswer = m21.group(2)
                
                myAnswerSheet_mixed.newQuestion(CorrectAnswer)
                myAnswerSheet_20.newQuestion(CorrectAnswer)
                myAnswerSheet_corpus.newQuestion(CorrectAnswer)
                CandRates = []
                CandRates_corpus = []
                CandRates_20 = []
                words_nearby = [] # prev and next 2 words
                
                Question = 'START START ' + myPreprocessor.getLine(Question.lower()) + ' END END'
                WordsinQestion = RWord.findall(Question)
                ixxxxx = WordsinQestion.index('xxxxx')
                words_nearby.append(WordsinQestion[ixxxxx - 1])
                words_nearby.append(WordsinQestion[ixxxxx - 2])
                words_nearby.append(WordsinQestion[ixxxxx + 1])
                words_nearby.append(WordsinQestion[ixxxxx + 2])
                
                for cand in Candidates:
                    Trigram20.compute()
                    Trigram20_r.compute()
                    # rate for four assumputions
                    x_corpus = []
                    x_20 = []
                    # bigram: previous one word
                    x_corpus.append(Trigram.get_p(one = words_nearby[0], two = cand))
                    x_20.append(Trigram20.get_p(one = words_nearby[0], two = cand))
                    # Trigram: previous two words   
                    x_corpus.append(Trigram.get_p(one = words_nearby[0], 
                                  two = words_nearby[1],
                                  three = cand))
                    x_20.append(Trigram20.get_p(one = words_nearby[0], 
                                  two = words_nearby[1],
                                  three = cand))
                    # Bigram: next one word
                    x_corpus.append(Trigram_r.get_p(one = words_nearby[2], two = cand))
                    x_20.append(Trigram20_r.get_p(one = words_nearby[2], two = cand))
                    # Trigram: next two words
                    x_corpus.append(Trigram_r.get_p(one = words_nearby[2], 
                                             two = words_nearby[3],
                                             three = cand))
                    x_20.append(Trigram20_r.get_p(one = words_nearby[2], 
                                             two = words_nearby[3],
                                             three = cand))
                    # weight the rates
                    CandRate_corpus = (np.dot(x_corpus, w_corpus))
                    CandRate_20 = (np.dot(x_20, w_20))
                    
                    CandRates_corpus.append(CandRate_corpus)
                    CandRates_20.append(CandRate_20)
                    CandRates.append(CandRate_corpus + CandRate_20)
                
                # choose the top rated candidate for answer                
                maxrate = np.max(CandRates)
                if maxrate == 0:
                    myAnswerSheet_mixed.submitAnswer(None)
                else:
                    i = 0
                    for r in CandRates:
                        if r == maxrate:
                            myAnswerSheet_mixed.submitAnswer(Candidates[i])
                            break
                        i += 1      
                        
                # choose from corpus
                maxrate_corpus = np.max(CandRates_corpus)
                if maxrate_corpus == 0:
                    myAnswerSheet_corpus.submitAnswer(None)
                else:
                    i = 0
                    for r in CandRates_corpus:
                        if r == maxrate_corpus:
                            myAnswerSheet_corpus.submitAnswer(Candidates[i])
                            break
                        i += 1
                        
                # choose from 20
                maxrate_20 = np.max(CandRates_20)
#                print('CandRates_20: \n', CandRates_20)
                if maxrate_20 == 0:
                    myAnswerSheet_20.submitAnswer(None)
                else:
                    i = 0
                    for r in CandRates_20:
                        if r == maxrate_20:
                            myAnswerSheet_20.submitAnswer(Candidates[i])
                            break
                        i += 1
        else:
            #blank line,  Reset
            Trigram20 = TrigramModel(isStop = isStop, isStem = isStem, isReversed = False)
            Trigram20_r = TrigramModel(isStop = isStop, isStem = isStem, isReversed = True)
            continue
    file.close()
    print('--Overall Answersheet---')
    myAnswerSheet_mixed.printResult()
    myAnswerSheet_mixed.printToFile('Overall')
    print('--Corpus Answersheet---')
    myAnswerSheet_corpus.printResult()
    myAnswerSheet_corpus.printToFile('corpus')
    print('--20sentences Answersheet---')
    myAnswerSheet_20.printResult()
    myAnswerSheet_20.printToFile('20sentences')
    print('----------------------')



        