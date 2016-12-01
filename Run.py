# -*- coding: utf-8 -*-
"""
Created on Mon Nov 28 16:22:50 2016

@author: ZHULI
"""
import random
import _thread
from LanguageModel import run_Trigram
from TrigramModel import Run_BuildData

def BuildDataSingleThreads():
    Run_BuildData(isPOS = False, isStop = False, isStem = False, isReversed = False)
    Run_BuildData(isPOS = False, isStop = False, isStem = False, isReversed = True)
#    Run_BuildData(isPOS = False, isStop = True, isStem = True, isReversed = False)
#    Run_BuildData(isPOS = False, isStop = True, isStem = True, isReversed = True)
#    Run_BuildData(isPOS = False, isStop = True, isStem = False, isReversed = False)
#    Run_BuildData(isPOS = False, isStop = True, isStem = False, isReversed = True)
#    Run_BuildData(isPOS = False, isStop = False, isStem = True, isReversed = False)
#    Run_BuildData(isPOS = False, isStop = False, isStem = True, isReversed = True)
#    Run_BuildData(isPOS = True, isStop = True, isStem = True, isReversed = False)
#    Run_BuildData(isPOS = True, isStop = True, isStem = True, isReversed = True)
#    Run_BuildData(isPOS = True, isStop = True, isStem = False, isReversed = False)
#    Run_BuildData(isPOS = True, isStop = True, isStem = False, isReversed = True)
#    Run_BuildData(isPOS = True, isStop = False, isStem = True, isReversed = False)
#    Run_BuildData(isPOS = True, isStop = False, isStem = True, isReversed = True)
#    Run_BuildData(isPOS = True, isStop = False, isStem = False, isReversed = False)
#    Run_BuildData(isPOS = True, isStop = False, isStem = False, isReversed = True)

def BuildDataThread(isReversed, Nothing):
    Run_BuildData(isPOS = True, isStop = False, isStem = False, isReversed = isReversed)
    Run_BuildData(isPOS = True, isStop = False, isStem = True, isReversed = isReversed)
    Run_BuildData(isPOS = True, isStop = True, isStem = False, isReversed = isReversed)
    Run_BuildData(isPOS = True, isStop = True, isStem = True, isReversed = isReversed)
    Run_BuildData(isPOS = False, isStop = False, isStem = False, isReversed = isReversed)
    Run_BuildData(isPOS = False, isStop = True, isStem = True, isReversed = isReversed)
    Run_BuildData(isPOS = False, isStop = True, isStem = False, isReversed = isReversed)
    Run_BuildData(isPOS = False, isStop = False, isStem = True, isReversed = isReversed)


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
        run_Trigram(True, True, filename)
        run_Trigram(True, False, filename)
        run_Trigram(False, True, filename)
        run_Trigram(False, False, filename)
        print('======================')
    
def RunTestMultiThreads():
    def run4conditions(filename, nothing):
        run_Trigram(True, True, filename)
        run_Trigram(True, False, filename)
        run_Trigram(False, True, filename)
        run_Trigram(False, False, filename)
        
    for filename in testFiles:
        _thread.start_new_thread(run4conditions, (filename, 1))
        
        
#Run_BuildData(isPOS = False, isStop = True, isStem = True, isReversed = False)        
        
#BuildDataSingleThreads()

#BuildDataTwoThreads()

#BuildDataMultiThreads()

RunTestSingleThread()

#RunTestMultiThreads()