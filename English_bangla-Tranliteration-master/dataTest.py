#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 11 17:28:14 2019

@author: hasan
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar  5 15:27:05 2019

@author: hasan
"""




import os
import string
import re
import numpy as np
import array
def load_doc(filename):
  # open the file as read only
  file = open(filename, mode="r", encoding="utf-8-sig")
  # read all text
  text = file.read()
  # close the file
  file.close()
  return text

#Get English and Bangla word list from a docname


unique_bangla_chars = set()
unique_banglish_chars = set()


def getEnglishAndBanglaWordList(docname):

    text = load_doc(docname)
    splittedLines = text.splitlines()
    lengthOfSplittedLines = len(splittedLines)

    engWords = []
    bngWords = []
    count1 = 0
    count2 = 0
    count3 = 0
    for i in range(0, lengthOfSplittedLines):
        line = splittedLines[i]
        word = line.split("\t")
        if(len(word) > 2):
            
            bw = word[0]
            ew = word[1]
            print(i+1, " : ", bw, " >>> ", ew, "\n")
            count2 = count2 + 1
        if(len(word) < 2):
            count1 = count1 + 1

        if(len(word) == 2):
            count3 = count3 + 1
            bangla_word = list(word[0])
            banglish_word = list(word[1])
            for c in bangla_word:
                
                if (c == '\xa0' or c=='\u200c' or c== '\u200d'):
                    print(str(bangla_word), ">>>>>>>>", (i+1))
                    continue
                
                unique_bangla_chars.add(c)

            for c in banglish_word:
                
                if (c == '\ufeff'):
                    print(str(banglish_word), ">>>>>>>>", (i+1))
                    continue
                
                unique_banglish_chars.add(c)
            


    print("Data less than 2 in a row: ", count1)
    print("Data greater than 2 in a row: ", count2)
    print("Data equal to 2 in a row: ", count3)
    print("Total line : ", count1 + count2 + count3)
    print("Total Data : ", i+1)

    print("Total Bangla chars : ", len(unique_bangla_chars))
    print("Total english chars : ", len(unique_banglish_chars))
    print(unique_bangla_chars)
    print("\n english chars: \n")
    print(unique_banglish_chars)


#getEnglishAndBanglaWordList("finalData.txt")

getEnglishAndBanglaWordList("mergedDataAll.txt")
