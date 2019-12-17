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
  file = open(filename, mode= "r" , encoding="utf-8-sig" )
  # read all text
  text = file.read()
  # close the file
  file.close()
  return text

#Get English and Bangla word list from a docname
def getEnglishAndBanglaWordList(docname):
    
    text = load_doc(docname)    
    splittedLines = text.splitlines()
    lengthOfSplittedLines = len(splittedLines)
    
    #print(lengthOfSplittedLines)
    
    
    #eng_word, bng_word = getEnglishAndBanglaSentences(splittedLines=splittedLines)
    
    
    engWords = []
    bngWords = []
    
    for i in range(0, lengthOfSplittedLines):     
        line= splittedLines[i]
        word = line.split("\t")
        if( len(word) == 2):
            bw = word[0]
            ew = word[1]
            engWords.append(ew)
            bngWords.append(bw)
            #print(bw, ">>",ew)

    #print(">>>", engWords,bngWords)
    return engWords, bngWords


ewlist, bwlist = getEnglishAndBanglaWordList("../Data/data.txt")
#ewlist, bwlist = getEnglishAndBanglaWordList("finalData.txt")

#print("aaa",len(ewlist),len(bwlist))
'''
for i in range(0, len(ewlist)):     
    print(">>>", ewlist[i],bwlist[i])
    
'''
encountered_words = {}
count_of_banglish_words = 0
for ew, bw in zip(ewlist, bwlist):
    #does not include repeated english word, includes only unique words
    if encountered_words.get(bw) == None:
        encountered_words[bw] = [ew]
        count_of_banglish_words = count_of_banglish_words + 1
    else:
        '''
        temp_banglish_word_list=encountered_words[bw]
        temp_banglish_word_list.append(ew)
        encountered_words[bw]=temp_banglish_word_list
        '''
        temp_banglish_word_list=encountered_words[bw]
        if ew in temp_banglish_word_list:
            continue
        else:
            temp_banglish_word_list.append(ew)
            encountered_words[bw]=temp_banglish_word_list
            count_of_banglish_words = count_of_banglish_words + 1
        
    
#print(encountered_words)

print("Unique Bangla words : ",len(encountered_words))

#print(">>>> ", len(ewlist),"   ",count_of_banglish_words, "   ",len(encountered_words))
mean_banglish_word = count_of_banglish_words / len(encountered_words)
print("Mean Banglish words : ",mean_banglish_word)

max_banglishWord=0
min_banglishWord=1000000


        
for key in encountered_words:
    #print(key)
    temp_banglish_word_list = encountered_words[key]
    
    
    if (max_banglishWord < len(temp_banglish_word_list)):
        max_banglishWord = len(temp_banglish_word_list)
        
    if(min_banglishWord > len(temp_banglish_word_list)):
        min_banglishWord = len(temp_banglish_word_list)
    
print("Maximum Banglish words : ",max_banglishWord)
print("Minimum Banglish words : ",min_banglishWord)


def checkWordFrequency(word):
    
    if encountered_words.get(word) == None:
        print("This word does not exist")
    else:
        temp_banglish_word_list = encountered_words[word]
        print(word, " word's banglish word frequency : ",len(temp_banglish_word_list))
        print("Banglish words are : ",temp_banglish_word_list)
    
while(True):
    bangla_word = input("Enter exit to close the program : \nEnter bangla word to know the frequency and banglish word list :")
    if(bangla_word == 'exit'):
        break
    checkWordFrequency(bangla_word)





