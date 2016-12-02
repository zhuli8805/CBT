# -*- coding: utf-8 -*-
"""
Created on Mon Nov 28 16:22:50 2016

@author: ZHULI
"""

import _thread
from LanguageModel import answer_Trigramsimple
from TrigramModel import Run_BuildData
from TrigramModel_WP import Run_BuildData_WP

def BuildDataSingleThreads():
    Run_BuildData(isStop = False, isStem = False, isReversed = False)
    Run_BuildData(isStop = False, isStem = False, isReversed = True)
#    Run_BuildData(isStop = True, isStem = True, isReversed = False)
#    Run_BuildData(isStop = True, isStem = True, isReversed = True)
#    Run_BuildData(isStop = True, isStem = False, isReversed = False)
#    Run_BuildData(isStop = True, isStem = False, isReversed = True)
#    Run_BuildData(isStop = False, isStem = True, isReversed = False)
#    Run_BuildData(isStop = False, isStem = True, isReversed = True)
#    Run_BuildData(isStop = True, isStem = True, isReversed = False)
#    Run_BuildData(isStop = True, isStem = True, isReversed = True)
#    Run_BuildData(isStop = True, isStem = False, isReversed = False)
#    Run_BuildData(isStop = True, isStem = False, isReversed = True)
#    Run_BuildData(isStop = False, isStem = True, isReversed = False)
#    Run_BuildData(isStop = False, isStem = True, isReversed = True)
#    Run_BuildData(isStop = False, isStem = False, isReversed = False)
#    Run_BuildData(isStop = False, isStem = False, isReversed = True)

def BuildDataThread(isReversed, Nothing):
    Run_BuildData(isStop = False, isStem = False, isReversed = isReversed)
    Run_BuildData(isStop = False, isStem = True, isReversed = isReversed)
    Run_BuildData(isStop = True, isStem = False, isReversed = isReversed)
    Run_BuildData(isStop = True, isStem = True, isReversed = isReversed)
    Run_BuildData(isStop = False, isStem = False, isReversed = isReversed)
    Run_BuildData(isStop = True, isStem = True, isReversed = isReversed)
    Run_BuildData(isStop = True, isStem = False, isReversed = isReversed)
    Run_BuildData(isStop = False, isStem = True, isReversed = isReversed)

def BuildDataTwoThreads():
    _thread.start_new_thread(BuildDataThread, (True, True))
    _thread.start_new_thread(BuildDataThread, (False, False))
  

def BuildDataMultiThreads():
    for isstop in [True, False]:
        for isstem in [True, False]:
            for isrev in [True, False]:
                _thread.start_new_thread(Run_BuildData, (False, isstop, isstem, isrev))
                
testFiles = [
             '..\..\..\..\CBTest Datasets\CBTest\data\cbtest_CN_test_2500ex.txt',
             '..\..\..\..\CBTest Datasets\CBTest\data\cbtest_NE_test_2500ex.txt',
             '..\..\..\..\CBTest Datasets\CBTest\data\cbtest_P_test_2500ex.txt',
             '..\..\..\..\CBTest Datasets\CBTest\data\cbtest_V_test_2500ex.txt']

def RunTestSingleThread():
    for filename in testFiles:
        answer_Trigramsimple(True, True, filename)
        answer_Trigramsimple(True, False, filename)
        answer_Trigramsimple(False, True, filename)
        answer_Trigramsimple(False, False, filename)
        print('======================')
    
def RunTestMultiThreads():
    def run4conditions(filename, nothing):
        answer_Trigramsimple(True, True, filename)
        answer_Trigramsimple(True, False, filename)
        answer_Trigramsimple(False, True, filename)
        answer_Trigramsimple(False, False, filename)        
    for filename in testFiles:
        _thread.start_new_thread(run4conditions, (filename, 1))
      
def BuildData_WP():
    for isPOS in [True, False]:
        for isStop in [True, False]:
            for isStem in [True, False]:
                Run_BuildData_WP(isPOS = isPOS, isStop = isStop, isStem = isStem, isReversed = False)
                Run_BuildData_WP(isPOS = isPOS, isStop = isStop, isStem = isStem, isReversed = True)
                
#Run_BuildData(isPOS = False, isStop = True, isStem = True, isReversed = False)        

#BuildDataSingleThreads()

#BuildDataTwoThreads()

#BuildDataMultiThreads()

BuildData_WP()

#RunTestSingleThread()

#RunTestMultiThreads()