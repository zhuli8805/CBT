# -*- coding: utf-8 -*-
"""
Created on Mon Nov 28 16:22:50 2016

@author: ZHULI
"""

import _thread
from AnswerSheet import AnswerSheet_oneTestFile
from TrigramAnswer import answer_Trigram_simple, answer_Trigram_WP
from TrigramSimple import Run_BuildData
from TrigramWP import Run_BuildData_WP

testFiles = [
             'CBTest Datasets\CBTest\data\cbtest_CN_test_2500ex.txt',
             'CBTest Datasets\CBTest\data\cbtest_NE_test_2500ex.txt',
             'CBTest Datasets\CBTest\data\cbtest_P_test_2500ex.txt',
             'CBTest Datasets\CBTest\data\cbtest_V_test_2500ex.txt'
            ]
            
def BuildDataSingleThreads():
    for isStop in [True, False]:
        for isStem in [True, False]:
            for isRev in [True, False]:
                Run_BuildData(isStop = isStop, isStem = isStem, isReversed = isRev)

def BuildDataThread(isReversed, Nothing):
    Run_BuildData(isStop = False, isStem = False, isReversed = isReversed)
    Run_BuildData(isStop = False, isStem = True, isReversed = isReversed)
    Run_BuildData(isStop = True, isStem = False, isReversed = isReversed)
    Run_BuildData(isStop = True, isStem = True, isReversed = isReversed)
    
def BuildDataTwoThreads():
    _thread.start_new_thread(BuildDataThread, (True, True))
    _thread.start_new_thread(BuildDataThread, (False, False))

def BuildDataMultiThreads():
    for isstop in [True, False]:
        for isstem in [True, False]:
            for isrev in [True, False]:
                _thread.start_new_thread(Run_BuildData, (False, isstop, isstem, isrev))

def BuildData_WP():
    for isPOS in [True, False]:
        for isStop in [True, False]:
            for isStem in [True, False]:
                Run_BuildData_WP(isPOS = isPOS, isStop = isStop, isStem = isStem, isReversed = False)
                Run_BuildData_WP(isPOS = isPOS, isStop = isStop, isStem = isStem, isReversed = True)

            
def RunTestAll():
    for isStop in [False, True]:
        for isStem in [False, True]:                
            testDict = {}
            for fileName in testFiles:
                testDict[fileName] =  AnswerSheet_oneTestFile(isStop = isStop, isStem = isStem, fileName = fileName)
            testDict = answer_Trigram_simple(isStop = isStop, isStem = isStem, testDict = testDict)
            testDict = answer_Trigram_WP(isStop = isStop, isStem = isStem, testDict = testDict)
            for answerSheet in testDict.values():
                print('Question Num =', len(answerSheet))
            print('<writing results..>')
            for answerSheet in testDict.values():
                answerSheet.printToFile()

if __name__ == '__main__':
    #BuildDataSingleThreads()    
    #BuildDataTwoThreads()    
    #BuildDataMultiThreads()    
    #BuildData_WP()  
    RunTestAll()