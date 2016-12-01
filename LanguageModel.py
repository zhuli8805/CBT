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
        self.answersheet = AnswerSheet(isStop = isStop， isStem = isStem, testFileName = testFileName)
        self.__isWP = isWP
        if self.__isWP:
            self.__modelA = TrigramModel_WP(isPOS = isPOS, isReversed = False, isStop = isStop, isStem = isStem)
            self.__modelB = TrigramModel_WP(isPOS = isPOS, isReversed = True, isStop = isStop, isStem = isStem)
        else:
            self.__modelA = TrigramModel_WP(isReversed = False, isStop = isStop, isStem = isStem)
            self.__modelB = TrigramModel_WP(isReversed = True, isStop = isStop, isStem = isStem)
        self.__modelA.load()
        self.__modelB.load()
        
    def answer(self, question, candidates):
        ratingA = self.__modelA.answer(question, candidates)
        ratingB = self.__modelB.answer(question, candidates)
        ratings = ratingA + ratingB
        return ratings
        
    def newQuestion(self, correctAnswer, question, candidates):
        self.answersheet.newQuestion(correctAnswer)
        
                
        
        if self.__isWP:
            pass
        else:
            pass
        ratings = self.answer(question, candidates)
        maxrate = np.max(ratings)
        if maxrate_corpus == 0:
            self.answersheet.submitAnswer(None)
        else:
            imax = ratings.index(maxrate)
            myAnswer = candidateList[imax]            
            self.answersheet.submitAnswer(myAnswer)
        return ratings
    
    def reset(self, testFileName)
        self.answersheet.reset(testFileName = testFileName)
        
class TrigramPair_20(Trigram):
    def __init__(self, isWP, isPOS, isStop, isStem, testFileName = None, wA = [1, 1, 1, 1], wB = [1, 1, 1, 1]):
        self.answersheet = AnswerSheet(isStop = isStop， isStem = isStem, testFileName = testFileName)
        self.__isWP = isWP
        if self.__isWP:
            self.__modelA = TrigramModel_WP(isPOS = isPOS, isReversed = False, isStop = isStop, isStem = isStem)
            self.__modelB = TrigramModel_WP(isPOS = isPOS, isReversed = True, isStop = isStop, isStem = isStem)
        else:
            self.__modelA = TrigramModel_WP(isReversed = False, isStop = isStop, isStem = isStem)
            self.__modelB = TrigramModel_WP(isReversed = True, isStop = isStop, isStem = isStem)
        
    def update(self, line):
        pass
    
    def reset(self):
        pass
    
    
            
def run_Trigram(isStop, isStem, filename):
#    print('----------------------')
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
    myAnswerSheet_mixed = AnswerSheet(filename, isStop, isStem)
    myAnswerSheet_corpus = AnswerSheet(filename, isStop, isStem)
    myAnswerSheet_20 = AnswerSheet(filename, isStop, isStem)
    
#    answerNum = 0
    for line in file:
        mLineNum = RLineNum.search(line)
        if(mLineNum):
    #        print (mLineNum)
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
#                print(Question)
                WordsinQestion = RWord.findall(Question)
                ixxxxx = WordsinQestion.index('xxxxx')
                words_nearby.append(WordsinQestion[ixxxxx - 1])
                words_nearby.append(WordsinQestion[ixxxxx - 2])
                words_nearby.append(WordsinQestion[ixxxxx + 1])
                words_nearby.append(WordsinQestion[ixxxxx + 2])
#                if words_nearby == ['START', 'START', 'END', 'END']:
#                    print('=======')
#                    print(line)
#                    print(m21.group(1))
#                    print(Question)
#                    print(words_nearby)
                
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
        #                    myAnswerSheet_mixed.submitAnswer(Candidates[random.randint(0, 9)]) # Random
        #                    print('answer:', i, Candidates[random.randint(0, 9)]) # Random
        #                    print(CandRates)
                            break
                        i += 1      
                        
                # choose from corpus
                maxrate_corpus = np.max(CandRates_corpus)
#                print('CandRates_corpus: \n', CandRates_corpus)
                if maxrate_corpus == 0:
                    myAnswerSheet_corpus.submitAnswer(None)
                else:
#                    answerNum += 1
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



        