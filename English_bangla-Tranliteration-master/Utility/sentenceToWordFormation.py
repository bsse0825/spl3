#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar  1 11:28:12 2019

@author: hasan
"""

import os
import string
import re
import numpy as np

def load_doc(filename):
  # open the file as read only
  file = open(filename, mode= "r" , encoding="utf-8-sig" )
  # read all text
  text = file.read()
  # close the file
  file.close()
  return text

def isEnglishSentence(sentence):
    
    if len(sentence) == 0:
        return False
    
    numberOfEnglishChars = 0

    for c in sentence:
        isEnglishLetter = re.match(r'[a-zA-Z0-9]', c)
        if (isEnglishLetter is None) == False:
            numberOfEnglishChars += 1
    
    if numberOfEnglishChars == 0:
        return False
    
    #print((numberOfEnglishChars/len(sentence)*100))
    if ((numberOfEnglishChars/len(sentence)*100) > 50):
        return True
    
    return False


#I don't know how to detect this.
def isBanglaSentence(sentence):
    
    
    if isEnglishSentence(sentence) == False:
        numberOfChar = 0
        
        for c in sentence:
            if c.isalpha():
                numberOfChar += 1
        
        if numberOfChar == 0:
            return False
        
        if (len(sentence)/numberOfChar)*100 > 10:
            return True
    else:
        return False
    
    
def getEnglishAndBanglaSentences(splittedLines):
    #prepare english and bangla sentences
    english_sentence_list = []
    bangla_sentence_list = []
    
    eng_sentence = ""
    bng_sentence = ""
    
    for line in splittedLines:
        if isEnglishSentence(line):
            eng_sentence = line
        elif isBanglaSentence(line):
            bng_sentence = line
            
        if len(eng_sentence) > 0 and len(bng_sentence) > 0:
            english_sentence_list.append(eng_sentence)
            bangla_sentence_list.append(bng_sentence)
            eng_sentence = ""
            bng_sentence = ""
    
    return english_sentence_list, bangla_sentence_list



# Get english and bangla sentences first
text = load_doc("../Dataset/chat-1.txt")
splittedLines = text.splitlines()

eng_s, ban_s = getEnglishAndBanglaSentences(splittedLines=splittedLines)



#print(eng_s[0])
#print(ban_s[0])
#print(len(eng_s))

#Get English and Bangla word list from a docname
def getEnglishAndBanglaWordList(docname):
    text = load_doc(docname)
    
    splittedLines = text.splitlines()
    lengthOfSplittedLines = len(splittedLines)
    eng_sentence, bng_sentence = getEnglishAndBanglaSentences(splittedLines=splittedLines)
    
    #print(eng_sentence[0], bng_sentence[0])
#    print(eng_sentence, bng_sentence)
    if (len(eng_sentence) == len(bng_sentence)) == False:
        print("This is a case that should not occur")
    
    engWords = []
    bngWords = []
    
#     print(eng_sentence)
    
    for i in range(0, len(eng_sentence)):
#         print(i, eng_sentence[i], bng_sentence[i])
        ew = eng_sentence[i].split(";")
        bw = bng_sentence[i].split(";")
        
        if (len(ew) != len(bw)):
            print("English - %s, bangla - %s, Count %d %d" % (ew, bw, len(ew), len(bw)))
        engWords.extend(ew)
        bngWords.extend(bw)
        
    return engWords, bngWords


ewlist, bwlist = getEnglishAndBanglaWordList("../Dataset/" + "chat-15.txt")



#print(ewlist[0])
#print(bwlist[0])

dataset_names = os.listdir("../Dataset")

english_word_list = []
bangla_word_list = []

for name in dataset_names:
    
    if (name.find(".txt") != -1):
        ewlist, bwlist = getEnglishAndBanglaWordList("../Dataset/" + name)
        english_word_list.extend(ewlist)
        bangla_word_list.extend(bwlist)
        
print(">>>>",len(english_word_list))
print(">>>>",len(bangla_word_list))


#Verify if the indexing is alright
print(english_word_list[40], bangla_word_list[40])
print(english_word_list[505], bangla_word_list[505])
print(english_word_list[5225], bangla_word_list[5225])
print(english_word_list[15000], bangla_word_list[15000])
print(english_word_list[22077], bangla_word_list[22077])



#CLEAN THE DATA
def cleanWord(word, isBangla):
    cleaned = ""
    for c in word:
        if c == '\ufeff' or c == '\u200c':
            continue
        if isBangla and not(re.match(r'[a-zA-Z৷।]', c) == None):
            continue
        if(re.match(r'[’‘“\'\":\-!@#$%^&?*\_/+,."("")"\\–” ]', c) == None):
            cleaned += c
            
    return cleaned
    
def shouldIncludeWord(word):
    if len(word) > 0:
        return True
    return False


def clean_word_list(current_ew_word_list, current_bw_word_list):
    cleaned_english_word_list = []
    cleaned_bangla_word_list = []
    encountered_words = {}

    for ew, bw in zip(current_ew_word_list, current_bw_word_list):
        #does not include repeated english word, includes only unique words
        if encountered_words.get(ew) == None:
            encountered_words[ew] = True
        else:
            continue

        if shouldIncludeWord(ew):
            cleaned_ew = cleanWord(ew, False).lower()
            cleaned_bw = cleanWord(bw, True)

            cleaned_english_word_list.append(cleaned_ew)
            cleaned_bangla_word_list.append(cleaned_bw)
    #print(len(encountered_words),len(cleaned_english_word_list),len(cleaned_bangla_word_list))
    
    return cleaned_english_word_list, cleaned_bangla_word_list


cleaned_english_words, cleaned_bangla_words = clean_word_list(english_word_list, bangla_word_list)

print("unique banglish word :",len(cleaned_english_words))
print("unique bangl word : ",len(cleaned_bangla_words))
print(cleaned_english_words[40], cleaned_bangla_words[40])


def save_word_pair_to_file(cleaned_english_words, cleaned_bangla_words):
    
    output_file = open('sentenceToWord.txt', 'w', encoding="utf-8-sig")
    
    for ew, bw in zip(cleaned_english_words, cleaned_bangla_words):
        output_file.write(bw+"\t"+ew+"\n" )

    output_file.close()


save_word_pair_to_file(cleaned_english_words, cleaned_bangla_words)