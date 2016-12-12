# -*- coding: utf-8 -*-
"""
Created on Thu Nov  3 13:15:51 2016

@author: acp16mh
"""

import re, sys
from random import randint

wordSearch=re.compile("\w+")
AnswerSearch = re.compile("[(\w+)\|]+\w+")
CorrectAnswer = re.compile("\s+(\w+)\s\s+")

docwords = {}
possibleAnswers = [] 
words = []
count = 0
DocCount = 1
NbFrqCorrect = 0
NbRandCorrect = 0

ResultsFile = open("ChildTestResults.csv", "w") #Will fail here if you have the file open 
ResultsFile.write("Document Number, Correct Answer, Most Frequent Answer, Most Frequent Correct?, Random Answer, Random Number Correct? \n")
ExportedData = str(DocCount)
with open ('TestTrain.txt', "r") as page:    
    for line in page:
        count+=1
        if count <= 20:  #reads in the first 20 lines and counts the number of times each word appears
            #print(count, ":", line)
            words = wordSearch.findall(line)
            for word in words:
                if word != str(count): #The lines start with their number, this removes that
                    word=word.lower()
                    if word in docwords:
                        docwords[word] +=1
                    else:
                        docwords[word] = 1
        elif count == 21:
            print(line)
            #Getting only the sentence 
            WordsInLine = AnswerSearch.findall(line)
            QSentence = ""
            for i in range(1, len(WordsInLine)-2):
                print(WordsInLine[i])
                QSentence +=WordsInLine[i] + " "
            print(QSentence)
            SenSplit = re.split("XX+", line)
            
            #Getting the answer, which is given in the text
            GivenAnswer = CorrectAnswer.findall(line)
            hold = ""
            for i in range(0,len(GivenAnswer)):
                hold += GivenAnswer[i]
            #print(hold)
            #Finding the answer given in the text
            GivenAnswerS = str(hold)
            #print(GivenAnswerS)
            ExportedData += "," + str(GivenAnswerS)
            
            #Getting the possible answers
            PossibleAnswer = AnswerSearch.findall(line)
            AllPoss = PossibleAnswer[len(PossibleAnswer)-1]            
            AllPossAns = wordSearch.findall(AllPoss)
            print(AllPossAns)
            #Best way I could find of getting only the possible answers
            
            #Most frequent method
            answercount = 0
            for word in AllPossAns:
                if word in docwords:
                    #print(word, docwords[word])
                    if docwords[word] > answercount:
                        answercount = docwords[word] 
                        FeqAnswer = word
            if answercount > 0:
                #print("\nThe most common possible answer is: ", FeqAnswer, "\nWith a count of: ", answercount)
                ExportedData += "," + str(FeqAnswer)
                if FeqAnswer == GivenAnswerS:
                    ExportedData += "," + "1"
                    NbFrqCorrect += 1
                else:
                    ExportedData += "," + "0"
                #print("\nThe full sentence is therefore: \n", SenSplit[0], answer, SenSplit[1])
            else:
                #print("None of the possible anwers appeared in the text")
                ExportedData += "," + "NA" + "," + "NA"
                
            #Random number method            
            randomWord = randint(0, len(AllPossAns)-1)
            #print("Random word chosen was:", AllPossAns[randomWord])
            ExportedData += "," + str(AllPossAns[randomWord])
            if AllPossAns[randomWord] == GivenAnswerS:
                ExportedData += "," + "1"
                NbRandCorrect += 1
            else:
                ExportedData += "," + "0"
            
            #Writing the data to the file    
            ExportedData += "\n"
            ResultsFile.write(ExportedData)
            #print(ExportedData)
        elif count == 22:  #Reads in the possible answers 
            print(DocCount, "documents done")            
            count = 0
            DocCount += 1
            docwords.clear()
            ExportedData = str(DocCount)
        else:
            #It should just never reach this point
            print("Houston we have a problem")
            sys.end()
            
ResultsFile.close()
FrqProb = NbFrqCorrect/DocCount
RandProb = NbRandCorrect/DocCount
print("The most frequent word got", NbFrqCorrect,"which gives the probablity of being correct as", FrqProb)
print("The random word got", NbRandCorrect, "which gives the probablity of being correct as", RandProb)
print("Thats all folks")
